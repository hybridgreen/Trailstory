import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function displayAlert(title: string, description: string) {
  return (
    <Alert>
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{description}</AlertDescription>
    </Alert>
  );
}
