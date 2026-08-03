import fs from "node:fs";
import path from "node:path";


export type RepositoryIndexEntry = {
  issue_id: string;
  publication_date: string;
  edition_code: string;
  topic_number: number;
  issue_title: string;
  rating: number | null;
  gs_paper: string | null;
  gs_subject: string | null;
  content_hash?: string | null;
};


export type KnowledgePoint = {
  number?: number;
  heading: string;
  explanation: string;
};


export type GSMapping = {
  display?: string;
  paper: string;
  subject: string;
  syllabus: string;
};


export type IssueRecord = {
  schema_version: string;
  issue_id: string;
  publication_date: string;
  edition_code: string;
  topic_number: number;
  issue_title: string;
  rating: number | null;
  editorial_sources: string[];
  gs_mapping: GSMapping;
  todays_question: string;
  recall_anchors: string[];
  knowledge_points: KnowledgePoint[];
  quick_facts: string[];
  key_takeaway: string;
  mains_question: string;
  mains_answer?: {
    paragraphs?: string[];
    full_text?: string;
  };
};


export type LatestEdition = {
  editionCode: string;
  publicationDate: string;
  issues: IssueRecord[];
};


/**
 * During local development, process.cwd() is normally:
 *
 * F:\Personal Projects\UPSC Issues by Kumar\website
 *
 * The permanent repository therefore exists one level above it.
 */
function getProjectRoot(): string {
  const currentDirectory = process.cwd();

  const possibleRoots = [
    path.resolve(currentDirectory, ".."),
    currentDirectory,
  ];

  for (const candidate of possibleRoots) {
    const repositoryIndex = path.join(
      candidate,
      "repository",
      "index.json",
    );

    if (fs.existsSync(repositoryIndex)) {
      return candidate;
    }
  }

  throw new Error(
    "Could not locate repository/index.json. " +
      "The website must remain inside the main UPSC project folder.",
  );
}


function readJsonFile<T>(filePath: string): T {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Required JSON file was not found: ${filePath}`);
  }

  const rawContent = fs.readFileSync(
    filePath,
    "utf-8",
  );

  return JSON.parse(rawContent) as T;
}


export function getRepositoryIndex(): RepositoryIndexEntry[] {
  const projectRoot = getProjectRoot();

  const indexPath = path.join(
    projectRoot,
    "repository",
    "index.json",
  );

  const entries = readJsonFile<RepositoryIndexEntry[]>(
    indexPath,
  );

  if (!Array.isArray(entries)) {
    throw new Error(
      "repository/index.json must contain a JSON array.",
    );
  }

  return entries;
}


export function getIssueById(
  issueId: string,
): IssueRecord | null {
  const projectRoot = getProjectRoot();

  const issuePath = path.join(
    projectRoot,
    "repository",
    "issues",
    `${issueId}.json`,
  );

  if (!fs.existsSync(issuePath)) {
    return null;
  }

  return readJsonFile<IssueRecord>(
    issuePath,
  );
}


export function getLatestEdition(): LatestEdition | null {
  const index = getRepositoryIndex();

  if (index.length === 0) {
    return null;
  }

  /*
   * Edition codes use YYMMDD:
   *
   * TUI-260803
   * TUI-260804
   *
   * This allows normal text sorting to identify the latest edition.
   */
  const sortedEntries = [...index].sort(
    (first, second) =>
      second.edition_code.localeCompare(
        first.edition_code,
      ) ||
      first.topic_number - second.topic_number,
  );

  const latestEditionCode =
    sortedEntries[0].edition_code;

  const latestEntries = sortedEntries
    .filter(
      (entry) =>
        entry.edition_code === latestEditionCode,
    )
    .sort(
      (first, second) =>
        first.topic_number - second.topic_number,
    );

  const issues = latestEntries
    .map((entry) => getIssueById(entry.issue_id))
    .filter(
      (issue): issue is IssueRecord =>
        issue !== null,
    );

  return {
    editionCode: latestEditionCode,
    publicationDate:
      latestEntries[0].publication_date,
    issues,
  };
}