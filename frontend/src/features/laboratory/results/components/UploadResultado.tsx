import { useRef } from "react";

import { Button } from "@/design-system";

const ACCEPT = ".pdf,.png,.jpg,.jpeg,.docx";

interface UploadResultadoProps {
  onUpload: (file: File, descricao: string) => void;
  isPending?: boolean;
  disabled?: boolean;
}

export function UploadResultado({ onUpload, isPending, disabled }: UploadResultadoProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const descRef = useRef<HTMLInputElement>(null);

  const handleSelect = () => {
    const file = inputRef.current?.files?.[0];
    if (!file || disabled) return;
    onUpload(file, descRef.current?.value ?? "");
    if (inputRef.current) inputRef.current.value = "";
    if (descRef.current) descRef.current.value = "";
  };

  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="flex-1">
        <label className="mb-1 block text-sm text-slate-600">Descrição (opcional)</label>
        <input
          ref={descRef}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          placeholder="Ex.: Laudo em PDF"
          disabled={disabled}
        />
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="hidden"
        disabled={disabled}
        onChange={handleSelect}
      />
      <Button
        type="button"
        variant="secondary"
        disabled={disabled || isPending}
        onClick={() => inputRef.current?.click()}
      >
        {isPending ? "A enviar..." : "Anexar ficheiro"}
      </Button>
      <p className="w-full text-xs text-slate-500">PDF, PNG, JPEG ou DOCX</p>
    </div>
  );
}
