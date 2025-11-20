import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { useState } from "react";

interface TripPhotosProps {
  photos: Record<string, string>; // { photo_id: s3_url }
  onDelete: (photoId: string) => Promise<void>;
}

export function TripPhotos({ photos, onDelete }: TripPhotosProps) {
  const [deleting, setDeleting] = useState<string | null>(null);

  const handleDelete = async (photoId: string) => {
    setDeleting(photoId);
    try {
      await onDelete(photoId);
    } finally {
      setDeleting(null);
    }
  };

  const photoEntries = Object.entries(photos);

  if (photoEntries.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {photoEntries.map(([photoId, url]) => (
        <div key={photoId} className="relative group">
          <div className="relative aspect-square overflow-hidden rounded-lg border-2 border-gray-200">
            <img
              src={url}
              alt={`Photo ${photoId}`}
              className="w-full h-full object-cover"
            />

            {/* Delete button overlay */}
            <div className="absolute inset-0 group-hover:bg-black group-hover:bg-opacity-40 transition-all flex items-center justify-center">
              <Button
                variant="destructive"
                size="icon"
                className="opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={() => handleDelete(photoId)}
                disabled={deleting === photoId}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
