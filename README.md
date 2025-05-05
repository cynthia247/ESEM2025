# How Do Community Smells Influence Self-Admitted Technical Debt in Machine Learning Projects?

### 
Community smells reflect poor organizational practices that often lead to socio-technical issues and the accumulation of Self-Admitted Technical Debt (SATD). While prior studies have explored these problems in general software systems, their interplay in machine learning (ML)-based projects remains largely underexamined. In this study, we investigated the prevalence of community smells and their relationship with SATD in open-source ML projects, analyzing data at the release level. 
First, we examined the prevalence of ten community smell types across the releases of 155 ML-based systems and found that community smells are widespread, exhibiting distinct distribution patterns across small, medium, and large projects.
Second, we detected SATD at the release level and applied statistical analysis to examine its correlation with community smells. Our results showed that certain smells, such as Radio Silence and Organizational Silos, are strongly correlated with higher SATD occurrences. 
Third, we considered the six identified types of SATD to determine which community smells are most associated with each debt category. Our analysis revealed authority- and communication-related smells often co-occur with persistent code and design debt. 
Finally, we analyzed how the community smells and SATD evolve over the releases, uncovering project size-dependent trends and shared trajectories. 
Our findings emphasize the importance of early detection and mitigation of socio-technical issues to maintain the long-term quality and sustainability of ML-based systems.

## Analyzing the Prevalence of Community Smells in ML projects
<ul>
    <li>Please consider Datasets/Selected_Repos-with-release.csv file to get the selected projects</li>
    <li>Apply **csDetector_New_Param** on the selected repositories. Details of running csDetector is available here - [https://github.com/Nuri22/csDetector]. For the modified version, please provide the <i>start_date</i> and <i>end_date</i> to analyze within a defined time period.  </li>
</ul>

## Investigating the Correlations between Community Smells and SATD
<ul>
    <li>Please consider **Scripts/1.extract_releases.py, Scripts/2.extract_comments.py and Scripts/3.SATD_detection.py** files to extract comments from the repositories for all the releases and detect the SATD instances. </li>
    <li>Apply mt-bert-satd-tool to detect the SATD instances from the extracted comments. Find details here - [https://github.com/zscszndxdxs/2023-MT-BERT-SATD] </li>
    <li>Please consider **Scripts #4 - #6** for investigating the correlations between community smells and SATD. </li>
</ul>

## Exploring the association between SATD types and Community Smells
<ul>
    <li>Please consider <a> [https://github.com/RISElabQueens/SATD_LLM] </a> model to detect the SATD types of the SATD instances </li>
    <li>Please consider **Scripts #9 - #11** for exploring the association between SATD types and Community Smells. </li>
</ul>

## Analyzing trends of community smells and SATD over releases
<ul>
    <li>Please consider **Scripts #13 - #14** for exploring the association between SATD types and Community Smells. </li>
</ul>
