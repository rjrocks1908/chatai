import { createBrowserRouter } from "react-router-dom";
import NotFoundPage from "../pages/NotFoundPage";
import { ChatPage } from "../pages/ChatPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: ChatPage,
  },
  {
    path: "*",
    Component: NotFoundPage,
  },
]);