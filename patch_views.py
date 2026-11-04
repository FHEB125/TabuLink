content = open('console/views.py', 'r', encoding='utf-8').read()
old = '''    role_key = _coordinator_role_for_user(request.user)
    event = get_object_or_404(_coordinator_events(request.user, role_key).select_related('program', 'category'), pk=event_id)'''
new = '''    event = get_object_or_404(Event.objects.select_related('program', 'category'), pk=event_id)
    role_key = _coordinator_role_for_user(request.user, event=event)
    event = get_object_or_404(_coordinator_events(request.user, role_key).select_related('program', 'category'), pk=event_id)'''
if old not in content:
    print('no')
else:
    content = content.replace(old, new)
    open('console/views.py', 'w', encoding='utf-8').write(content)
    print('ok')
