import re

from django.core.management.base import BaseCommand, CommandError

from college.models import Department, ClassInstance, Turn, Class, TurnInstance, Place, Laboratory, Building
from clip import models as clip


class Command(BaseCommand):
    help = 'Generates events to match the turn instances'

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='+', type=int)
        parser.add_argument('period', nargs='+', type=int)

    def handle(self, *args, **options):
        year = options['year'][0]
        period = clip.Period.objects.get(id=options['period'][0])

        for clip_place in clip.Classroom.objects.all():
            lab_exp = re.compile('[Ll]ab[\.]? (?P<name>.*)$')
            clip_building: clip.Building = clip_place.building
            try:
                building: Building = clip_building.building
            except Exception:
                raise CommandError('Please *MANUALLY* link buildings to CLIP buildings before running this.')

            if not hasattr(clip_place, 'place'):
                if 'lab' in clip_place.name.lower():
                    lab_matches = lab_exp.search(clip_place.name)
                    lab_name = lab_matches.group('name')
                    corresponding_place = Laboratory(name=lab_name, building=building, clip_place=clip_place)
                else:  # default to a generic place (Classrooms and auditoriums are manually assigned)
                    corresponding_place = Place(name=clip_place.name, building=building, clip_place=clip_place)
                corresponding_place.save()
                print(f'Created classroom {corresponding_place}')

        institution = clip.Institution.objects.get(abbreviation='FCT')
        for clip_department in clip.Department.objects.filter(institution=institution):
            if not hasattr(clip_department, 'department'):
                corresponding_department = Department(name=clip_department.name, clip_department=clip_department)
                corresponding_department.save()
                print(f'Created department {corresponding_department}')

        for clip_class_instance in clip.ClassInstance.objects.filter(year=year, period=period):
            clip_class: clip.Class = clip_class_instance.parent
            # Create class in case it doesn't exist
            if hasattr(clip_class, 'related_class'):
                corresponding_class = clip_class.related_class
            else:
                corresponding_class = Class(name=clip_class.name, clip_class=clip_class,
                                            abbreviation=clip_class.abbreviation,
                                            department=clip_class.department.department, credits=clip_class.ects)
                corresponding_class.save()
                print(f'Created class {corresponding_class}')

            # Create corresponding class instance
            if hasattr(clip_class_instance, 'class_instance'):
                corresponding_class_instance = clip_class_instance.class_instance
            else:
                corresponding_class_instance = ClassInstance(
                    parent=corresponding_class, period=period, year=year, clip_class_instance=clip_class_instance)
                corresponding_class_instance.save()
                print(f'Created class instance {corresponding_class_instance}')

            for clip_turn in clip_class_instance.turns.all():
                if hasattr(clip_turn, 'turn'):
                    corresponding_turn: Turn = clip_turn.turn
                else:
                    corresponding_turn = Turn(clip_turn=clip_turn, turn_type=clip_turn.type, number=clip_turn.number,
                                              class_instance=corresponding_class_instance)
                    corresponding_turn.save()

                for clip_turn_instance in clip_turn.instances.all():
                    if not hasattr(clip_turn_instance, 'turn_instance'):
                        if hasattr(clip_turn_instance, 'start') and hasattr(clip_turn_instance, 'end'):
                            duration = clip_turn_instance.end - clip_turn_instance.start
                        else:
                            duration = None
                        if hasattr(clip_turn_instance, 'classroom'):
                            # ...       ClipTurnInstance   ClipClassroom Classroom
                            place = clip_turn_instance.classroom.place
                        else:
                            place = None

                        corresponding_turn_instance = TurnInstance(
                            turn=corresponding_turn, clip_turn_instance=clip_turn_instance,
                            weekday=clip_turn_instance.weekday, start=clip_turn_instance.start,
                            duration=duration, place=place)
                        corresponding_turn_instance.save()
                        print(f'Created turn instance {corresponding_turn_instance}')
