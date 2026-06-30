import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AMIS - Marketing Intelligence Dashboard",
  description: "Agentic Marketing Intelligence System Dashboard",
};

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "📊" },
  { href: "/articles", label: "Articles", icon: "📄" },
  { href: "/platforms", label: "Platforms", icon: "📱" },
  { href: "/audiences", label: "Audiences", icon: "👥" },
  { href: "/campaigns", label: "Campaigns", icon: "🎯" },
  { href: "/topics", label: "Topics", icon: "🏷️" },
  { href: "/graph", label: "Knowledge Graph", icon: "🔗" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen">
          <nav className="w-56 bg-gray-900 text-white p-4 flex flex-col shrink-0">
            <div className="text-lg font-bold mb-6 px-2">AMIS Dashboard</div>
            <div className="flex flex-col gap-1">
              {NAV_ITEMS.map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm"
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </a>
              ))}
            </div>
          </nav>
          <main className="flex-1 overflow-y-auto bg-gray-50">{children}</main>
        </div>
      </body>
    </html>
  );
}
