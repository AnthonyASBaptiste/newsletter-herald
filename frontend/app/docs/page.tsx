import React from 'react';
import fs from 'fs';
import path from 'path';
import DocsTabs from './DocsTabs';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: "Documentation Center - SALLTO Herald",
  description: "User manuals, operational guidelines, and development changelogs for the SALLTO Herald platform.",
};

export default async function DocsPage() {
  const docsDir = path.join(process.cwd(), 'docs');
  const adminGuidePath = path.join(docsDir, 'ADMIN_GUIDE.md');
  const changelogPath = path.join(docsDir, 'CHANGELOG.md');

  let adminGuide = '';
  let changelog = '';

  try {
    adminGuide = fs.readFileSync(adminGuidePath, 'utf8');
  } catch (err) {
    console.error("Failed to read ADMIN_GUIDE.md:", err);
    adminGuide = "# Error\nFailed to load the Admin Manual. Please check that `docs/ADMIN_GUIDE.md` exists.";
  }

  try {
    changelog = fs.readFileSync(changelogPath, 'utf8');
  } catch (err) {
    console.error("Failed to read CHANGELOG.md:", err);
    changelog = "# Error\nFailed to load the Changelog. Please check that `docs/CHANGELOG.md` exists.";
  }

  return <DocsTabs adminGuide={adminGuide} changelog={changelog} />;
}
