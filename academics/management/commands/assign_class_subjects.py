from django.core.management.base import BaseCommand, CommandError

from academics.models import AcademicYear, Class, Subject, ClassSubject
from teachers.models import Teacher

DEFAULT_SUBJECTS = [
    "Mathematics",
    "English Language",
    "Integrated Science",
    "Social Studies",
    "Religious & Moral Education",
    "Creative Arts",
    "Career Technology",
    "ICT",
    "Gonja",
]


def get_academic_year(name: str | None):
    if name:
        ay = AcademicYear.objects.filter(name=name).first()
        if not ay:
            raise CommandError(f"AcademicYear '{name}' not found")
        return ay
    ay = AcademicYear.objects.filter(is_current=True).first()
    if not ay:
        raise CommandError("No AcademicYear marked is_current=True")
    return ay


def pick_teacher_for_subject(subj: Subject):
    return (
        Teacher.objects.filter(subjects=subj)
        .select_related("user")
        .order_by("id")
        .first()
    )


def assign_for_class(cls: Class, subject_names: list[str]):
    created = 0
    updated = 0
    skipped = 0
    for subj_name in subject_names:
        subj = Subject.objects.filter(name__iexact=subj_name).first()
        if not subj:
            skipped += 1
            continue
        teacher = pick_teacher_for_subject(subj)
        cs, made = ClassSubject.objects.get_or_create(
            class_name=cls,
            subject=subj,
            defaults={"teacher": teacher},
        )
        if made:
            created += 1
        else:
            if cs.teacher != teacher:
                cs.teacher = teacher
                cs.save(update_fields=["teacher"])
                updated += 1
    return created, updated, skipped


class Command(BaseCommand):
    help = "Assign subjects to classes for an academic year (creates/updates ClassSubject with available teachers)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--classes",
            dest="classes",
            default="Basic 7,Basic 8,Basic 9",
            help="Comma-separated class names (default: Basic 7,Basic 8,Basic 9)",
        )
        parser.add_argument(
            "--subjects",
            dest="subjects",
            default=",".join(DEFAULT_SUBJECTS),
            help="Comma-separated subject names (default: core list)",
        )
        parser.add_argument(
            "--year",
            dest="year_name",
            default=None,
            help="AcademicYear name; defaults to current is_current=True",
        )

    def handle(self, *args, **options):
        year_name = options["year_name"]
        ay = get_academic_year(year_name)

        class_names = [c.strip() for c in options["classes"].split(",") if c.strip()]
        subject_names = [s.strip() for s in options["subjects"].split(",") if s.strip()]

        classes = {}
        for name in class_names:
            cls, _ = Class.objects.get_or_create(name=name, academic_year=ay)
            classes[name] = cls

        total_created = 0
        total_updated = 0
        total_skipped = 0

        for cls in classes.values():
            c, u, s = assign_for_class(cls, subject_names)
            total_created += c
            total_updated += u
            total_skipped += s

        self.stdout.write(
            self.style.SUCCESS(
                f"Assigned subjects for {len(classes)} classes in {ay.name}. Created: {total_created}, Updated: {total_updated}, Subjects missing: {total_skipped}"
            )
        )
