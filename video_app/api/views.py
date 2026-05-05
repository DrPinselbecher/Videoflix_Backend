from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from video_app.models import Video

from .serializers import VideoListSerializer


class VideoListView(ListAPIView):
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoListSerializer
    permission_classes = [IsAuthenticated]


class HLSPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str):
        if resolution not in ["480p", "720p", "1080p"]:
            raise Http404("Invalid resolution.")

        playlist_path = Path(settings.MEDIA_ROOT) / "hls" / str(movie_id) / f"{resolution}.m3u8"

        if not playlist_path.exists():
            raise Http404("Playlist not found.")

        return FileResponse(
            playlist_path.open("rb"),
            content_type="application/vnd.apple.mpegurl",
        )


class HLSSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str, segment: str):
        if resolution not in ["480p", "720p", "1080p"]:
            raise Http404("Invalid resolution.")

        if not segment.endswith(".ts") or "/" in segment or "\\" in segment:
            raise Http404("Invalid segment.")

        if not segment.startswith(f"{resolution}_"):
            raise Http404("Invalid segment.")

        segment_path = Path(settings.MEDIA_ROOT) / "hls" / str(movie_id) / segment

        if not segment_path.exists():
            raise Http404("Segment not found.")

        return FileResponse(
            segment_path.open("rb"),
            content_type="video/MP2T",
        )