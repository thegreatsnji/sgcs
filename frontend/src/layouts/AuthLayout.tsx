import { Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 via-white to-slate-100 px-4">
      <div className="w-full max-w-md">
        <Outlet />
      </div>
    </div>
  );
}
