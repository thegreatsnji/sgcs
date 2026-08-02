import { IconBell, IconCalendar, IconPatients } from "@/components/icons";
import { Badge, EmptyState } from "@/design-system";
import {
  ACTIVITY_TONE_CLASSES,
  formatReceptionActivityDescription,
  formatReceptionActivityTime,
  getReceptionActivityMeta,
  getUserInitials,
  type ReceptionActivityItem,
} from "@/features/reception/utils/formatReceptionActivity";

function ActivityIcon({ action }: { action: string }) {
  const className = "h-5 w-5";
  switch (action) {
    case "RECEPTION_CHECK_IN":
      return <IconPatients className={className} />;
    case "RECEPTION_STATUS_CHANGE":
      return <IconBell className={className} />;
    case "RECEPTION_ASSIGN_DOCTOR":
    case "RECEPTION_REFERRAL":
      return <IconCalendar className={className} />;
    default:
      return <IconPatients className={className} />;
  }
}

interface ReceptionActivityFeedProps {
  items: ReceptionActivityItem[];
  limit?: number;
  emptyTitle?: string;
  emptyDescription?: string;
}

export function ReceptionActivityFeed({
  items,
  limit = 10,
  emptyTitle = "Sem actividade recente",
  emptyDescription = "Os movimentos na receção aparecerão aqui em tempo real.",
}: ReceptionActivityFeedProps) {
  const visible = items.slice(0, limit);

  if (visible.length === 0) {
    return (
      <EmptyState
        title={emptyTitle}
        description={emptyDescription}
        icon={<IconPatients className="mx-auto h-10 w-10 opacity-40" />}
      />
    );
  }

  return (
    <ul className="divide-y divide-border">
      {visible.map((item, index) => {
        const meta = getReceptionActivityMeta(item.action);
        const tone = ACTIVITY_TONE_CLASSES[meta.tone];
        const description = formatReceptionActivityDescription(item.description);

        return (
          <li key={`${item.action}-${item.created_at}-${index}`} className="flex gap-4 py-4 first:pt-0 last:pb-0">
            <div
              className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${tone.icon}`}
              aria-hidden
            >
              <ActivityIcon action={item.action} />
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <Badge variant={tone.badge}>{meta.label}</Badge>
                <time className="text-xs font-medium text-text-muted tabular-nums">
                  {formatReceptionActivityTime(item.created_at)}
                </time>
              </div>

              <p className="mt-2 text-sm leading-relaxed text-text">{description}</p>

              <div className="mt-2 flex items-center gap-2">
                <span
                  className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-surface-muted text-[10px] font-bold text-text-muted"
                  aria-hidden
                >
                  {getUserInitials(item.user)}
                </span>
                <span className="truncate text-xs text-text-muted">{item.user}</span>
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
