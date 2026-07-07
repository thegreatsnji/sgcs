import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { Card } from "@/design-system";
import { ExpenseForm } from "@/features/finance/components/ExpenseForm";
import { FinanceSubNav } from "@/features/finance/components/FinanceSubNav";
import { financeService } from "@/services/finance/finance.service";

export function ExpenseFormPage() {
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: financeService.createExpense,
    onSuccess: () => void navigate("/finance/expenses"),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Nova despesa</h2>
        <p className="mt-1 text-slate-600">Registar uma nova despesa da clínica.</p>
      </div>
      <FinanceSubNav />
      <Card title="Dados da despesa">
        <ExpenseForm
          isPending={mutation.isPending}
          onSubmit={(values) =>
            mutation.mutate({
              fornecedor: values.fornecedor,
              categoria: values.categoria,
              valor: Number(values.valor),
              descricao: values.descricao,
              data: values.data,
            })
          }
        />
      </Card>
    </div>
  );
}
