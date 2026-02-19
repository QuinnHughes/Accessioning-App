import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Projects from "./pages/Projects";
import EmptyShelves from "./pages/EmptyShelves";
import Accessioning from "./pages/Accessioning";
import BatchPrinting from "./pages/BatchPrinting";
import UploadExport from "./pages/UploadExport";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="projects" element={<Projects />} />
          <Route path="empty-shelves" element={<EmptyShelves />} />
          <Route path="accessioning" element={<Accessioning />} />
          <Route path="batch-print" element={<BatchPrinting />} />
          <Route path="upload" element={<UploadExport />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
