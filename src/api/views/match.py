from itertools import chain
from operator import attrgetter

from rest_framework import filters
from rest_framework.decorators import list_route
from rest_framework.response import Response

from core.models import Match

from .base import TokenRequiredModelViewSet
from ..serializers import MatchSerializer


class MatchViewSet(TokenRequiredModelViewSet):

    serializer_class = MatchSerializer
    queryset = Match.objects.all()
    permissions = []
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('winner', 'loser')

    @list_route(methods=['get'])
    def head_to_head(self, request, pk=None):
        """Return the results of head to heads between two players."""
        player1 = request.query_params.get('player1')
        player2 = request.query_params.get('player2')

        if player1 is None or player2 is None:
            return None

        player1_wins = self.queryset.filter(winner=player1, loser=player2)
        player2_wins = self.queryset.filter(winner=player2, loser=player1)

        # combine the two querysets, ordered by the most recent game,
        # and put the last ten results in a nice string.
        all_games = list(chain(player1_wins, player2_wins))
        ordered_games = sorted(all_games, key=attrgetter('date'), reverse=True)
        limited_games = ordered_games[:10]
        serialized_matches = MatchSerializer(limited_games, many=True).data

        results = {
            player1: player1_wins.count(),
            player2: player2_wins.count(),
            'history': serialized_matches,
            'history_count': len(serialized_matches)
        }

        return Response(results)
