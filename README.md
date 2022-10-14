# testlink.xml-to-testrail.csv
Script that formats xml files export from testlink to csv import a file for testrail.

Faced with the problem of mass export of test cases from testlink to testrail, but did not find automated ways to speed up the work. I wrote it myself, I will be glad if it will be useful to someone

# Usage:
1. Export **testsuite** of the project or project branches from the testlink.
2. Run `python xml_to_csv.py -i <file_name>.xml`.
3. As a result, output files with testsuite branches or just test cases will be created in the directory where the script was executed.
4. During the import of *.csv files, we import them one by one together with config.cfg so that all the ticks and mapping are set automatically correctly.

# Work scenario:

#### Event 1:

> 1. We export the entire project from the testlink.
> 2. Run the script and specify the export file.
> 3. We get files with project branches.

#### Event 2:
> 4. If the file weight exceeds 1mb or does not load, then export the project branch and run the script for it.
> 5. Import the remaining branches.
> 6. A heavy branch will be split into branches inside it (files).
> 7. Import a root file called output_rot_testcases. Create a section for that very huge branch.
> 8. Import the remaining files and specify the section that was created.

#### Event 3:
> 4. Import all branches (*.csv files)
