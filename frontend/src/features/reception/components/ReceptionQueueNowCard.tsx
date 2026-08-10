import { Link } from "react-router-dom";

import { IconPatients } from "@/components/icons";
import { UI_COPY } from "@/constants/uiCopy";
import { Button, Card, EmptyState } from "@/design-system";
import { ReceptionQueuePreviewList } from "@/features/reception/components/ReceptionQueuePreviewList";
import type { ReceptionQueuePreviewEntry } from "@/features/reception/components/ReceptionQueuePreviewList";

export function ReceptionQueueNowCard({
  entries,
}: {
  entries: ReceptionQueuePreviewEntry[];
}) {
  const copy = UI_COPY.reception;

  return (
    <Card
      title={copy.queueSection}
      footer={
        entries.length > 0 ? (
          <Link to="/reception/queue">
            <Button type="button" variant="ghost" size="sm">{copy.openQueue}</Button>
          </Link>
        ) : undefined
      }
    >
      {entries.length === 0 ? (
        <EmptyState
          title={copy.queueEmpty}
          description={copy.queueEmptyHint}
          icon={<IconPatients className="mx-auto h-10 w-10 opacity-40" />}
        />
      ) : (
        <ReceptionQueuePreviewList entries={entries.slice(0, 8)} />
      )}
    </Card>
  );
}
