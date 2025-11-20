import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { X, Star } from "lucide-react";

interface PhotoUploadPreviewProps {
  files: File[];
  previewUrls: string[];
  thumbnailIndex: number | null;
  onDelete: (index: number) => void;
  onSetThumbnail: (index: number) => void;
}

export function PhotoPreview({
  files,
  previewUrls,
  thumbnailIndex,
  onDelete,
  onSetThumbnail,
}: PhotoUploadPreviewProps) {
  console.log(previewUrls);
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {previewUrls.map((url, index) => (
        <div key={index} className="relative group">
          <div className="relative aspect-square overflow-hidden rounded-lg border-2 border-gray-200">
            <img
              src={url}
              alt={files[index].name}
              className="w-full h-full object-cover"
            />

            {/* Overlay with buttons - shows on hover */}
            <div className="absolute inset-0 bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center gap-2">
              <Button
                variant="destructive"
                size="icon"
                className="opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={() => onDelete(index)}
              >
                <X className="h-4 w-4" />
              </Button>

              <Button
                variant={thumbnailIndex === index ? "default" : "secondary"}
                size="icon"
                className="opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={() => onSetThumbnail(index)}
              >
                <Star
                  className="h-4 w-4"
                  fill={thumbnailIndex === index ? "currentColor" : "none"}
                />
              </Button>
            </div>
          </div>

          {/* Thumbnail badge */}
          {thumbnailIndex === index && (
            <Badge className="absolute top-2 right-2 bg-yellow-500">
              <Star className="h-3 w-3 mr-1" fill="currentColor" />
              Thumbnail
            </Badge>
          )}

          {/* File name */}
          <p className="text-xs text-muted-foreground mt-1 truncate">
            {files[index].name}
          </p>
        </div>
      ))}
    </div>
  );
}
