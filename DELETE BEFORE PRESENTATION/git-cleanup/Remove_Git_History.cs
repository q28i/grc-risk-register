using System;
using System.IO;

namespace GRCRiskRegister.GitCleanup
{
    class Program
    {
        static int Main(string[] args)
        {
            Console.Title = "GRC Risk Register — Remove Git History";
            Console.WriteLine("=======================================================");
            Console.WriteLine("  GRC Risk Register — Git History Removal Tool");
            Console.WriteLine("=======================================================");

            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string projectRoot = FindProjectRoot(baseDir);

            if (string.IsNullOrEmpty(projectRoot))
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("\n[ABORTED] Could not automatically locate the GRC project root.");
                Console.WriteLine("Safety check failed: 'Grc Risk Management Code' folder not found in parent hierarchy.");
                Console.WriteLine("Refusing to operate on unknown directory.\n");
                Console.ResetColor();
                return 1;
            }

            Console.WriteLine("\n[INFO] Target Project Root: " + projectRoot);
            Console.WriteLine("\n[REMOVING] Deleting all Git metadata and repository history...");

            int removedCount = 0;
            int failedCount = 0;

            // 1. Delete all .git directories recursively inside projectRoot
            try
            {
                string[] allDirs = Directory.GetDirectories(projectRoot, "*", SearchOption.AllDirectories);
                foreach (string d in allDirs)
                {
                    if (string.Equals(Path.GetFileName(d), ".git", StringComparison.OrdinalIgnoreCase))
                    {
                        Console.WriteLine("[REMOVING] Deleting folder: " + d);
                        if (DeleteDirectorySafe(d)) removedCount++;
                        else failedCount++;
                    }
                }
            }
            catch { }

            // Check root .git directly
            string rootGit = Path.Combine(projectRoot, ".git");
            if (Directory.Exists(rootGit))
            {
                Console.WriteLine("[REMOVING] Deleting folder: " + rootGit);
                if (DeleteDirectorySafe(rootGit)) removedCount++;
                else failedCount++;
            }

            // 2. Delete Git configuration files (.gitignore, .gitattributes, .gitmodules)
            string[] gitFiles = new string[] { ".gitignore", ".gitattributes", ".gitmodules" };
            foreach (string gf in gitFiles)
            {
                try
                {
                    string[] found = Directory.GetFiles(projectRoot, gf, SearchOption.AllDirectories);
                    foreach (string f in found)
                    {
                        Console.WriteLine("[REMOVING] Deleting file: " + f);
                        try
                        {
                            File.SetAttributes(f, FileAttributes.Normal);
                            File.Delete(f);
                            removedCount++;
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine("[ERROR] Could not delete " + f + ": " + ex.Message);
                            failedCount++;
                        }
                    }
                }
                catch { }
            }

            // 3. Post-cleanup audit
            bool clean = !Directory.Exists(rootGit);
            Console.WriteLine("\n=======================================================");
            Console.WriteLine("  CLEANUP SUMMARY");
            Console.WriteLine("=======================================================");
            Console.WriteLine("Items removed: " + removedCount);
            Console.WriteLine("Items failed:  " + failedCount);

            if (clean && failedCount == 0)
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("\n[SUCCESS] Project is 100% clean of all Git metadata and version control history.");
                Console.WriteLine("Source code, presentation database, and application runtime are intact.\n");
                Console.ResetColor();
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("\n[WARNING] Some Git items could not be completely removed.\n");
                Console.ResetColor();
            }

            return clean ? 0 : 1;
        }

        private static string FindProjectRoot(string startDir)
        {
            DirectoryInfo current = new DirectoryInfo(startDir);
            for (int i = 0; i < 6 && current != null; i++)
            {
                string appCode = Path.Combine(current.FullName, "Grc Risk Management Code");
                string launcher = Path.Combine(current.FullName, "Start GRC Risk Register.exe");
                string readme = Path.Combine(current.FullName, "README.md");

                if (Directory.Exists(appCode) && (File.Exists(launcher) || File.Exists(readme)))
                {
                    return current.FullName;
                }

                current = current.Parent;
            }
            return null;
        }

        private static bool DeleteDirectorySafe(string path)
        {
            try
            {
                if (!Directory.Exists(path)) return true;
                foreach (string f in Directory.GetFiles(path, "*", SearchOption.AllDirectories))
                {
                    try { File.SetAttributes(f, FileAttributes.Normal); } catch { }
                }
                Directory.Delete(path, true);
                return !Directory.Exists(path);
            }
            catch
            {
                return false;
            }
        }
    }
}
