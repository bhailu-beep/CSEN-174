// Wraps every page on the site: loads the styles and puts the Header at the top.
import "./globals.css";
import Header from "@/components/Header";

export const metadata = { title: "CompleteC", description: "Practice C++ one exercise at a time" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><Header />{children}</body></html>;
}
