import { RouterProvider } from "react-router-dom";

import { router } from "@/routes/index";

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
