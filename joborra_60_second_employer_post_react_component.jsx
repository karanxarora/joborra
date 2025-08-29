import React, { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Wand2, Send, CheckCircle2, Eye } from "lucide-react";

/**
 * EmployerFastPost
 * Single-file component for ultra-fast job posting (<2 mins) for the Joborra MVP.
 * - Minimal fields (title, location, type, pay, email)
 * - AI-style auto-description generator (client-side template)
 * - One-click Preview & Publish
 * - Sends payload to a (placeholder) /api/jobs route for persistence (e.g., Airtable)
 * - For pilot: forwards applications to employerEmail (no dashboard required)
 *
 * How to use:
 * 1) Drop <EmployerFastPost /> into a page (e.g., app/employers/post/page.tsx)
 * 2) Implement /api/jobs (Next.js route) to upsert into Airtable (or your DB) and
 *    set email routing for applications.
 */
export default function EmployerFastPost() {
  const [form, setForm] = useState({
    companyName: "",
    abn: "",
    logoUrl: "",
    title: "",
    location: "",
    employmentType: "Casual",
    pay: "",
    employerEmail: "",
    internationalFriendly: true,
    description: "",
  });

  const [drafting, setDrafting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showPreview, setShowPreview] = useState(true);
  const [publishedId, setPublishedId] = useState<string | null>(null);

  const handle = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));

  const generatedDescription = useMemo(() => {
    return generateDescription({
      title: form.title,
      type: form.employmentType,
      location: form.location,
      intlFriendly: form.internationalFriendly,
    });
  }, [form.title, form.employmentType, form.location, form.internationalFriendly]);

  const description = form.description?.trim() ? form.description : generatedDescription;

  async function onGenerateClick() {
    setDrafting(true);
    // For MVP we do client-side templating (no external API required)
    await new Promise((r) => setTimeout(r, 350));
    setDrafting(false);
  }

  async function onPublish() {
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        description,
        source: "joborra-fast-post",
        status: "active",
        // suggested pilot defaults
        autoExpireDays: 30,
        createdAt: new Date().toISOString(),
      };

      // POST to your Next.js API route. Implement persistence there (e.g., Airtable).
      const res = await fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Failed to publish");
      const data = await res.json();
      setPublishedId(data?.id || "ok");
    } catch (e) {
      console.error(e);
      alert("Something went wrong while publishing. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-8">
      <div className="grid md:grid-cols-2 gap-6">
        {/* Left: Minimal Form */}
        <Card className="shadow-lg rounded-2xl">
          <CardHeader>
            <CardTitle className="text-2xl">Post a Job in 60 seconds</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">Provide the essentials — we’ll auto-write the rest and handle student-visa compliance text.</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Company name</Label>
                <Input placeholder="Acme Retail Pty Ltd" value={form.companyName} onChange={(e) => handle("companyName", e.target.value)} />
              </div>
              <div>
                <Label>ABN</Label>
                <Input placeholder="12 345 678 901" value={form.abn} onChange={(e) => handle("abn", e.target.value)} />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Company logo (URL)</Label>
                <Input placeholder="https://.../logo.png" value={form.logoUrl} onChange={(e) => handle("logoUrl", e.target.value)} />
              </div>
              <div>
                <Label>HR/Recruitment email (applications forwarded here)</Label>
                <Input type="email" placeholder="jobs@acme.com" value={form.employerEmail} onChange={(e) => handle("employerEmail", e.target.value)} />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Job title</Label>
                <Input placeholder="Retail Assistant" value={form.title} onChange={(e) => handle("title", e.target.value)} />
              </div>
              <div>
                <Label>Location</Label>
                <Input placeholder="Newcastle NSW" value={form.location} onChange={(e) => handle("location", e.target.value)} />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Employment type</Label>
                <Select value={form.employmentType} onValueChange={(v) => handle("employmentType", v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Casual">Casual</SelectItem>
                    <SelectItem value="Part-time">Part-time</SelectItem>
                    <SelectItem value="Full-time">Full-time</SelectItem>
                    <SelectItem value="Internship">Internship</SelectItem>
                    <SelectItem value="Contract">Contract</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Pay / Rate (optional)</Label>
                <Input placeholder="$28–$34/hr" value={form.pay} onChange={(e) => handle("pay", e.target.value)} />
              </div>
            </div>

            <div className="flex items-center justify-between rounded-xl border p-3">
              <div>
                <Label className="font-medium">International-student friendly</Label>
                <p className="text-xs text-muted-foreground">We’ll add the correct visa-compliance note to the ad.</p>
              </div>
              <Switch checked={form.internationalFriendly} onCheckedChange={(v) => handle("internationalFriendly", v)} />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Job description</Label>
                <Button type="button" variant="secondary" onClick={onGenerateClick} disabled={drafting} className="gap-2">
                  {drafting ? <Loader2 className="h-4 w-4 animate-spin"/> : <Wand2 className="h-4 w-4"/>}
                  Auto-generate
                </Button>
              </div>
              <Textarea rows={8} placeholder="We’ll auto-draft from your title, type, and location. You can edit if needed."
                value={form.description} onChange={(e) => handle("description", e.target.value)} />
              <p className="text-xs text-muted-foreground">Tip: Leave blank to use the generated draft. Edit only if you want changes.</p>
            </div>

            <div className="flex gap-3">
              <Button type="button" variant="outline" className="gap-2" onClick={() => setShowPreview((s) => !s)}>
                <Eye className="h-4 w-4"/> {showPreview ? "Hide" : "Show"} preview
              </Button>
              <Button type="button" onClick={onPublish} disabled={submitting} className="gap-2">
                {submitting ? <Loader2 className="h-4 w-4 animate-spin"/> : <Send className="h-4 w-4"/>}
                Publish
              </Button>
              {publishedId && (
                <div className="flex items-center gap-1 text-green-600 text-sm">
                  <CheckCircle2 className="h-4 w-4"/> Published!
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Right: Live Preview */}
        {showPreview && (
          <Card className="shadow-lg rounded-2xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-muted overflow-hidden">
                  {form.logoUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={form.logoUrl} alt="logo" className="h-10 w-10 object-cover" />
                  ) : (
                    <span className="text-sm text-muted-foreground">Logo</span>
                  )}
                </span>
                {form.title || "Job title"}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div><span className="font-medium">Company:</span> {form.companyName || "—"}</div>
                <div><span className="font-medium">Location:</span> {form.location || "—"}</div>
                <div><span className="font-medium">Type:</span> {form.employmentType}</div>
                <div><span className="font-medium">Pay:</span> {form.pay || "—"}</div>
              </div>
              <div className="prose prose-sm max-w-none">
                <h4 className="font-semibold">About the role</h4>
                <p className="whitespace-pre-wrap">{description}</p>
              </div>
              {form.internationalFriendly && (
                <div className="rounded-xl bg-emerald-50 p-3 text-sm">
                  <strong>International-student friendly.</strong> This employer welcomes international students in line with visa work conditions. Hours and duties must align with current Department of Home Affairs settings.
                </div>
              )}
              <div className="text-xs text-muted-foreground">Applications will be forwarded to <span className="font-mono">{form.employerEmail || "[HR email]"}</span>.</div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

// --- Simple client-side description generator for the pilot ---
function generateDescription({ title, type, location, intlFriendly }: { title: string; type: string; location: string; intlFriendly: boolean; }) {
  const cleanTitle = title?.trim() || "Retail Assistant";
  const cleanType = type || "Casual";
  const cleanLoc = location?.trim() || "Newcastle, NSW";

  const bullets = [
    "Welcome customers and provide friendly, efficient service",
    "Maintain store presentation and restock shelves as needed",
    "Operate POS and handle basic cash/card transactions",
    "Collaborate with team to meet daily KPIs",
  ];

  const quals = [
    "Great communication and a helpful attitude",
    "Reliable and punctual with attention to detail",
    "Available to work a flexible roster (including weekends if needed)",
  ];

  const visa = intlFriendly
    ? "\n\nThis role is suitable for international students. We follow current Department of Home Affairs work-rights settings."
    : "";

  return (
    `${cleanTitle} (${cleanType}) — ${cleanLoc}\n\n` +
    `We’re looking for a ${cleanTitle.toLowerCase()} to join our team. In this role you will:` +
    "\n\n• " + bullets.join("\n• ") +
    "\n\nYou’ll thrive if you have:" +
    "\n\n• " + quals.join("\n• ") +
    (visa ? visa : "") +
    "\n\nPay: Competitive and aligned with applicable awards.\nStart: ASAP.\n\nHow to apply: Submit your resume via Joborra. Shortlisted candidates will be contacted by email."
  );
}
