import re
import hashlib
import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError


_INVISIBLE_MARKS_RE = re.compile(r"[\ufeff\u200e\u200f\u202a-\u202e\u2066-\u2069]")
IT_MEMBER_USERNAMES = ['s20330', '250479', '230022', '140287', '111075', 'ithelpdesk']
IT_MAINTAIN_GROUP_NAME = 'IT maintain users'


def strip_invisible_marks(value: str) -> str:
    """
    Some upstream identity sources (e.g. directory/DB) can include invisible
    direction marks/BOM that end up rendering as "weird language" prefixes.
    """
    if not value:
        return ""
    return _INVISIBLE_MARKS_RE.sub("", str(value)).strip()


def get_it_maintain_group():
    from django.contrib.auth.models import Group as AuthGroup

    group, _ = AuthGroup.objects.get_or_create(name=IT_MAINTAIN_GROUP_NAME)
    return group


def get_it_member_usernames():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    dynamic_usernames = User.objects.filter(
        groups__name=IT_MAINTAIN_GROUP_NAME,
        is_active=True
    ).values_list('username', flat=True)
    return list(dict.fromkeys(IT_MEMBER_USERNAMES + sorted(dynamic_usernames)))


def is_it_member_user(user):
    if not user or not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser or user.username in IT_MEMBER_USERNAMES:
        return True

    return user.groups.filter(name=IT_MAINTAIN_GROUP_NAME).exists()


def is_protected_it_member(user):
    return bool(user and user.username in IT_MEMBER_USERNAMES)


def process_uploaded_file(uploaded_file, image_quality=65, max_image_size=(1280, 1280)):
    """
    Return a compressed file plus metadata. Images are reduced before storage;
    other files keep their original bytes so previews/downloads keep working.
    """
    original_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    original_size = len(original_bytes)
    file_hash = hashlib.sha256(original_bytes).hexdigest()
    original_name = uploaded_file.name or 'upload'
    processed_bytes = original_bytes
    processed_name = original_name
    was_compressed = False

    try:
        image = Image.open(BytesIO(original_bytes))
        image.load()
        image.thumbnail(max_image_size, Image.Resampling.LANCZOS)

        output = BytesIO()
        has_alpha = image.mode in ('RGBA', 'LA') or (
            image.mode == 'P' and 'transparency' in image.info
        )

        if has_alpha:
            image.save(output, format='PNG', optimize=True)
            extension = '.png'
        else:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(output, format='JPEG', optimize=True, quality=image_quality)
            extension = '.jpg'

        candidate_bytes = output.getvalue()
        if candidate_bytes and len(candidate_bytes) < original_size:
            processed_bytes = candidate_bytes
            processed_name = f"{os.path.splitext(original_name)[0]}_compressed{extension}"
            was_compressed = True
    except (UnidentifiedImageError, OSError):
        pass

    return {
        'file': ContentFile(processed_bytes, name=processed_name),
        'sha256': file_hash,
        'original_size': original_size,
        'compressed_size': len(processed_bytes),
        'was_compressed': was_compressed,
    }
