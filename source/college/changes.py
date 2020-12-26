from django.db.models import Max
from college import models as m


def singular_modification_for(entity):
    """
    Function meant to be used with a last_modified decorator to provide a date for an object of a given class.
    :param entity: The class of the object.
    :return: A function which returns the last modification date.
    """
    return lambda request, **args: _singular_modification(entity, args)


def _singular_modification(entity, args):
    """
    Concrete version of singular_modification_for.
    :param entity: The class of the object.
    :param args: A dictionary that must have a single value, the object identifier
    :return: The object last modification date.
    """
    if len(args) != 1:
        raise Exception("A singular_modification_for cannot be applied into views with more than one arg."
                        f"Was called with: {args}")
    try:
        return entity.objects.only('last_save').get(id=next(iter(args.values()))).last_save
    except entity.DoesNotExist:
        pass


def plural_modification_for(entity):
    """
    Function meant to be used with a last_modified decorator to provide a last change date for a given class.
    :param entity: The class being checked.
    :return: A function which returns the last modification date.
    """
    return lambda request: entity.objects.aggregate(Max('last_save'))['last_save__max']


def last_class_instance_modification(_, instance_id, **kwargs):
    try:
        return m.ClassInstance.objects.only('last_save').get(id=instance_id).last_save
    except m.ClassInstance.DoesNotExist:
        pass


def last_class_question_modification(_, class_id):
    # TODO finish, this is not enough to tell if there have been modifications
    try:
        return \
        m.Class.objects.only('last_save').annotate().get(id=class_id).linked_questions.aggregate(Max('timestamp'))[
            'timestamp__max']
    except m.Class.DoesNotExist:
        pass
