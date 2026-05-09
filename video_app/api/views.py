from django.http import FileResponse, Http404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from video_app.models import Video
from video_app.utils import (
    HLS_PLAYLIST_CONTENT_TYPE,
    HLS_SEGMENT_CONTENT_TYPE,
    get_hls_playlist_path,
    get_hls_segment_path,
    is_valid_hls_resolution,
    is_valid_hls_segment,
)

from .serializers import VideoListSerializer


class VideoListView(ListAPIView):
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoListSerializer
    permission_classes = [IsAuthenticated]


class HLSPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str):
        if not is_valid_hls_resolution(resolution):
            raise Http404("Invalid resolution.")

        playlist_path = get_hls_playlist_path(movie_id, resolution)

        if not playlist_path.exists():
            raise Http404("Playlist not found.")

        return FileResponse(
            playlist_path.open("rb"),
            content_type=HLS_PLAYLIST_CONTENT_TYPE,
        )


class HLSSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str, segment: str):
        if not is_valid_hls_resolution(resolution):
            raise Http404("Invalid resolution.")

        if not is_valid_hls_segment(resolution, segment):
            raise Http404("Invalid segment.")

        segment_path = get_hls_segment_path(movie_id, segment)

        if not segment_path.exists():
            raise Http404("Segment not found.")

        return FileResponse(
            segment_path.open("rb"),
            content_type=HLS_SEGMENT_CONTENT_TYPE,
        )