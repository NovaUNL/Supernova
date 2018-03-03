from django.core.management.base import BaseCommand, CommandError
from kleep.models import Period, Student, StudentClipStudent, TurnStudents, Enrollment, ClipEnrollment


class Command(BaseCommand):
    help = 'Generates events to match the turn instances'

    def add_arguments(self, parser):
        parser.add_argument('student_id', nargs='+', type=int)
        parser.add_argument('year', nargs='+', type=int)
        parser.add_argument('period', nargs='+', type=int)

    def handle(self, *args, **options):
        student = Student.objects.get(id=options['student_id'][0])
        year = options['year'][0]  # TODO apply filter
        period = Period.objects.get(id=options['period'][0])  # TODO apply filter

        for clip_student in student.crawled_students.all():
            for clip_turn in clip_student.clipturn_set.all():  # TODO filter
                if hasattr(clip_turn, 'turn') and \
                        not TurnStudents.objects.filter(student=student, turn=clip_turn.turn).exists():
                    class_instance = clip_turn.turn.class_instance
                    clip_enrollment = ClipEnrollment.objects.get(student=clip_student,
                                                                 class_instance=class_instance.clip_class_instance)
                    if not Enrollment.objects.filter(student=student, class_instance=class_instance,
                                                     clip_enrollment=clip_enrollment).exists():
                        Enrollment(student=student, class_instance=class_instance,
                                   clip_enrollment=clip_enrollment).save()
                        print(f'Enrolled student {student} to {class_instance}')

                    # TurnStudents(student=student, turn=clip_turn.turn).save()
                    print(f'Added turn {clip_turn.turn} to student {student}')
