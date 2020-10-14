import io
from functools import reduce
from django.core.files import File
from django.db.models import Q

from college import models as m


class TeacherPipeline(object):
    def process_item(self, item, spider):
        origin = item.get('origin')
        image = item.get('image_data', None)
        image_ext = item.get('image_ext', None)
        name = item.get('name').replace('.', '')
        url = item.get('url', None)
        ext = item.get('ext', None)
        rank = item.get('rank', None)
        email = item.get('email', None)

        department_abbr = origin.split('.')[1]
        name_filter = reduce(lambda x, y: x & y, [Q(name__contains=word) for word in name.split(' ')])
        matches = m.Teacher.objects.filter(name_filter).all()
        if len(matches) == 0:
            print("Unknown teacher")
            return
        elif len(matches) > 1:
            print("Unknown teacher")
            return
        else:
            teacher = matches[0]
            departments = teacher.departments.all()
            print(f"{name} (found in {origin}) matched against\n{teacher.name} ({departments})")
            print(f"{name} {department_abbr} => {teacher.departments.all()})")

        if email is not None:
            teacher.email = email
        if ext is not None:
            teacher.phone = f',{ext}'
        if url is not None:
            teacher.url = url
        if rank is not None:
            if 'atedr' in rank:
                teacher.rank_id = 1
            elif 'ssociad' in rank:
                teacher.rank_id = 2
            elif 'uxil' in rank:
                teacher.rank_id = 3
            elif 'ssist' in rank:
                teacher.rank_id = 4
            elif 'onvid' in rank:
                teacher.rank_id = 5
            elif 'bilad' in rank:
                teacher.rank_id = 6
            else:
                print("Weird rank")

        if image is not None:
            teacher.picture.save(f'pic.{image_ext}', File(io.BytesIO(image)))

        teacher.save()
        return item
