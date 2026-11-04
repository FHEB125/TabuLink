"""Read-only production diagnostic for the High Jump results-page report.

Run this against the PRODUCTION database (Render shell or locally with the
production environment variables loaded):

    python diagnose_high_jump_results.py

It prints only structural facts - event ids, names, programs, scopes, row
counts and statuses. It never prints credentials and never writes, updates or
deletes anything. Use it to find which High Jump event actually holds the
adviser registrations, scores and rankings, and whether the event shown on the
results page (program=1&event=26) is the same event the records are attached to.
"""
import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tabulink.settings')
sys.path.insert(0, os.getcwd())
django.setup()

from events.catalog import is_individual_sport_name  # noqa: E402
from events.models import Event  # noqa: E402
from programs.models import ParticipantSubmission, Program  # noqa: E402
from scores.models import GameResult, Score, SpecialEventResult  # noqa: E402


def event_line(event):
    scores = Score.objects.filter(event=event)
    special = SpecialEventResult.objects.filter(event=event)
    games = GameResult.objects.filter(game__event=event)
    roster = event.participating_participants.all()
    submissions = ParticipantSubmission.objects.filter(event=event)
    lines = [
        '  event id=%s program=%s(%s) name=%r type=%s scope=%s division=%r '
        'category=%s active=%s scheduled=%s' % (
            event.id, event.program_id, event.program.name if event.program_id else '?',
            event.name, event.event_type, event.participant_scope, event.division,
            event.category.name if event.category_id else None,
            event.is_active, event.scheduled_date,
        ),
        '    roster(active participant rows)=%d  adviser submissions=%d' % (
            roster.filter(is_active=True, team__is_active=True).count(),
            submissions.count(),
        ),
        '    scores by status=%s' % _counts(scores, 'status'),
        '    special results by status=%s  (verified/final=%d)' % (
            _counts(special, 'status'),
            special.filter(status__in=['VERIFIED', 'FINAL']).count(),
        ),
        '    game results=%d' % games.count(),
    ]
    if event.event_type == 'NON_JUDGING' and is_individual_sport_name(event.name) \
            and event.participant_scope != 'INDIVIDUAL':
        lines.append(
            '    !! MISCLASSIFIED: individual track event with scope=%r - '
            'rankings will NOT appear in standings until scope is INDIVIDUAL'
            % event.participant_scope,
        )
    return '\n'.join(lines)


def _counts(queryset, field):
    from django.db.models import Count
    return dict(
        queryset.values_list(field)
        .order_by(field)
        .annotate(total=Count('pk'))
        .values_list(field, 'total')
    )


def main():
    print('== PROGRAMS ==')
    for program in Program.objects.all().order_by('id'):
        print('  id=%s name=%r active=%s' % (program.id, program.name, program.is_active))

    high_jump_events = Event.objects.filter(name__icontains='high jump').select_related(
        'program', 'category',
    ).order_by('program_id', 'id')
    print('\n== EVENTS named like High Jump ==')
    found = False
    for event in high_jump_events:
        found = True
        print(event_line(event))
    if not found:
        print('  (none)')

    print('\n== EVENT id=26 exactly ==')
    event_26 = Event.objects.filter(pk=26).select_related('program', 'category').first()
    if event_26 is None:
        print('  no event with id=26')
    else:
        print(event_line(event_26))

    print('\n== ALL INDIVIDUAL ATHLETICS EVENTS (by catalog name) ==')
    athletics_found = False
    for event in Event.objects.select_related('program', 'category').order_by('program_id', 'id'):
        if event.event_type == 'NON_JUDGING' and is_individual_sport_name(event.name):
            athletics_found = True
            print(event_line(event))
    if not athletics_found:
        print('  (none)')

    print('\n== OTHER EVENTS WITH HIGH-JUMP-LIKE DATA ==')
    # Scores or rankings attached to an event NOT named High Jump, in case the
    # submissions were recorded against the wrong event entirely.
    score_events = (
        Score.objects.values_list('event_id', flat=True).distinct()
    )
    special_events = (
        SpecialEventResult.objects.values_list('event_id', flat=True).distinct()
    )
    suspicious_ids = set(score_events) | set(special_events)
    for event in Event.objects.filter(pk__in=suspicious_ids).exclude(
        name__icontains='high jump',
    ).select_related('program', 'category').order_by('program_id', 'id'):
        n_scores = Score.objects.filter(event=event).count()
        n_special = SpecialEventResult.objects.filter(event=event).count()
        if n_scores or n_special:
            print(
                '  event id=%s program=%s name=%r type=%s scope=%s '
                'scores=%d special_results=%d' % (
                    event.id, event.program_id, event.name, event.event_type,
                    event.participant_scope, n_scores, n_special,
                )
            )

    print('\nDone. No data was modified.')


if __name__ == '__main__':
    main()
