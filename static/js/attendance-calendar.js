document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('attendanceCalendar');
    const classFilter = document.getElementById('classFilter');
    const tooltipEl = document.getElementById('calendarTooltip');

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
        },
        events: {
            url: '/attendance/api/attendance-data/',
            extraParams: function() {
                return {
                    class_id: classFilter.value
                };
            },
            failure: function() {
                alert('There was an error while fetching attendance data!');
            }
        },
        eventMouseEnter: function(info) {
            const props = info.event.extendedProps;
            const date = info.event.start;

            tooltipEl.querySelector('.tooltip-date').innerHTML = date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            tooltipEl.querySelector('.tooltip-body').innerHTML = `
                <p><strong>Total Students:</strong> ${props.total}</p>
                <p class="present"><strong>Present:</strong> ${props.present} (${props.percentage}%)</p>
                <p class="absent"><strong>Absent:</strong> ${props.absent}</p>
            `;
            
            tooltipEl.style.display = 'block';
            
            // Position tooltip
            const rect = info.el.getBoundingClientRect();
            tooltipEl.style.left = `${rect.left + window.scrollX + rect.width / 2 - tooltipEl.offsetWidth / 2}px`;
            tooltipEl.style.top = `${rect.top + window.scrollY - tooltipEl.offsetHeight - 5}px`;
        },
        eventMouseLeave: function(info) {
            tooltipEl.style.display = 'none';
        },
        dateClick: function(info) {
            // You can add functionality to view details for a specific day
            console.log('Clicked on: ' + info.dateStr);
        },
        loading: function(isLoading) {
            if (isLoading) {
                // You can show a loader
            } else {
                // You can hide the loader
            }
        }
    });

    calendar.render();

    // Refetch events when the class filter changes
    classFilter.addEventListener('change', function() {
        calendar.refetchEvents();
    });
});
