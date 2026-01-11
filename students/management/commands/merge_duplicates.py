
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum, Count, Q
from accounts.models import User
from students.models import Student, Grade, StudentExerciseScore, Attendance
from teachers.models import Teacher, DutyAssignment
from academics.models import ClassSubject, Class
from finance.models import StudentFee, Payment
import sys

class Command(BaseCommand):
    help = 'Merges duplicate student and teacher records based on name similarity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Run without interactive confirmation',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(self.style.WARNING("This will permanently merge duplicate records based on full name matching."))
            confirm = input("Type 'YES' to proceed: ")
            if confirm != 'YES':
                self.stdout.write(self.style.ERROR("Cancelled."))
                return

        self.merge_students()
        self.merge_teachers()

    def get_full_name_key(self, user):
        # Combine first and last, lowercase, strip extra spaces
        full = f"{user.first_name} {user.last_name}"
        return " ".join(full.lower().split())

    def merge_students(self):
        self.stdout.write("Finding duplicate students...")
        # Group by normalized full name
        all_students = Student.objects.select_related('user').all()
        grouped = {}
        for s in all_students:
            key = self.get_full_name_key(s.user)
            if not key: continue
            if key not in grouped: grouped[key] = []
            grouped[key].append(s)

        duplicates_found = 0
        merged_count = 0

        for key, students in grouped.items():
            if len(students) < 2:
                continue

            duplicates_found += 1
            self.stdout.write(f"\nProcessing duplicate group: '{key}' ({len(students)} records)")

            # Rank students to find primary
            # Strategy: Prefer records with Grades > ExerciseScores > Attendance > ID
            ranked = []
            for s in students:
                score = 0
                score += s.grade_set.count() * 10
                score += s.studentexercisescore_set.count() * 5
                score += s.attendance_set.count() * 1
                if s.user.is_active: score += 50 # Prefer active users
                ranked.append((score, s))
            
            # Sort desc by score, then asc by ID (older first)
            ranked.sort(key=lambda x: (-x[0], x[1].id))
            
            primary = ranked[0][1]
            dupes = [x[1] for x in ranked[1:]]

            self.stdout.write(f"  > Primary: ID {primary.id} (Score {ranked[0][0]}) - {primary.admission_number}")
            
            with transaction.atomic():
                for dup in dupes:
                    self.stdout.write(f"  > Merging ID {dup.id} ({dup.admission_number})...")
                    
                    # 1. Merge Grades
                    for g in dup.grade_set.all():
                        exists = Grade.objects.filter(
                            student=primary,
                            subject=g.subject,
                            academic_year=g.academic_year,
                            term=g.term
                        ).first()
                        
                        if exists:
                            if g.total_score > exists.total_score:
                                exists.class_score = g.class_score
                                exists.exams_score = g.exams_score
                                exists.save()
                            g.delete()
                        else:
                            g.student = primary
                            g.save()
                    
                    # 2. Merge Exercise Scores
                    for es in dup.studentexercisescore_set.all():
                        exists = StudentExerciseScore.objects.filter(
                            student=primary,
                            exercise=es.exercise
                        ).first()
                        
                        if exists:
                            if es.score > exists.score:
                                exists.score = es.score
                                exists.save()
                            es.delete()
                        else:
                            es.student = primary
                            es.save()

                    # 3. Merge Attendance
                    for att in dup.attendance_set.all():
                        exists = Attendance.objects.filter(
                            student=primary,
                            date=att.date
                        ).exists()
                        
                        if exists:
                            att.delete()
                        else:
                            att.student = primary
                            att.save()

                    # 4. Merge Finance (Fees & Payments)
                    for dup_fee in dup.fees.all():
                        primary_fee = StudentFee.objects.filter(
                            student=primary, 
                            fee_structure=dup_fee.fee_structure
                        ).first()
                        
                        if primary_fee:
                            for p in dup_fee.payments.all():
                                p.student_fee = primary_fee
                                p.save()
                            primary_fee.update_status()
                            dup_fee.delete()
                        else:
                            dup_fee.student = primary
                            dup_fee.save()

                    # 5. Cleanup
                    u = dup.user
                    dup.delete()
                    u.delete()
                    merged_count += 1

        self.stdout.write(self.style.SUCCESS(f"\nCompleted! Merged {merged_count} duplicate student records."))


    def merge_teachers(self):
        self.stdout.write("\nFinding duplicate teachers...")
        all_teachers = Teacher.objects.select_related('user').all()
        grouped = {}
        for t in all_teachers:
            key = self.get_full_name_key(t.user)
            if not key: continue
            if key not in grouped: grouped[key] = []
            grouped[key].append(t)

        duplicates_found = 0
        merged_count = 0

        for key, teachers in grouped.items():
            if len(teachers) < 2:
                continue

            duplicates_found += 1
            self.stdout.write(f"\nProcessing duplicate teacher group: '{key}' ({len(teachers)} records)")

            ranked = sorted(teachers, key=lambda x: (not x.user.is_active, x.id))
            primary = ranked[0]
            dupes = ranked[1:]

            self.stdout.write(f"  > Primary: ID {primary.id} ({primary.employee_id})")

            with transaction.atomic():
                for dup in dupes:
                    self.stdout.write(f"  > Merging ID {dup.id} ({dup.employee_id})...")
                    
                    Class.objects.filter(class_teacher=dup).update(class_teacher=primary)
                    ClassSubject.objects.filter(teacher=dup).update(teacher=primary)
                    
                    for da in dup.dutyassignment_set.all():
                        exists = DutyAssignment.objects.filter(week=da.week, teacher=primary).exists()
                        if exists:
                            da.delete()
                        else:
                            da.teacher = primary
                            da.save()

                    if hasattr(dup.user, 'assigned_activities'):
                        for activity in dup.user.assigned_activities.all():
                            activity.assigned_staff.add(primary.user)
                            activity.assigned_staff.remove(dup.user)

                    u = dup.user
                    dup.delete()
                    u.delete()
                    merged_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Completed! Merged {merged_count} duplicate teacher records."))
