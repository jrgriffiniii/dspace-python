<?xml version="1.0" encoding="UTF-8"?>
<!-- 
    This stylesheet should be used to extract metadata into the directory
      and file structure that DSpace requies for import.
      
      Author:  Mark Ratliff
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:saxon="http://icl.com/saxon" extension-element-prefixes="saxon">

    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
    
    <!-- Define the folder where the output XML files will be written -->
    <xsl:variable name="outputfolder">/Users/ratliff/Programming/DataSpace_Imports/ETDs/trunk/Theses/legacy_import/importfiles</xsl:variable>
    
    <xsl:variable name="smallcase" select="'abcdefghijklmnopqrstuvwxyz'" />
    <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />

    <!-- Do not preserve whitespace or new lines from XML file. -->
    <xsl:strip-space elements="*"/>
    
    <xsl:template match="/">
        <ListOfTheses>
            <xsl:apply-templates select="dataroot/Theses"/>
        </ListOfTheses>
    </xsl:template>

    <xsl:template match="Theses">
        <xsl:variable name="foldername" select="Dcode1"/>

        <!-- Write ea dublin_core.xml file for each thesis -->
        <!-- Collect theses into folders named after department -->
        <saxon:output
            href="{$outputfolder}/{$foldername}/{position()}/dublin_core.xml">
            <xsl:attribute name="counter">
                <xsl:value-of select="position()"/>
            </xsl:attribute>

            <!-- Metadata elements in Dublin Core schema -->
            <dublin_core schema="dc">
                <!-- Strip newlines from the Title using the translate function. -->
                <!-- TODO:  remove white space after newline.  Example ThesisNo 2963 AAR/10030/dublin_core.xml -->
                <dcvalue element="title" qualifier="none"><xsl:value-of select="normalize-space(Title)"/></dcvalue>
                <!-- dcvalue element="title" qualifier="none"><xsl:value-of select="translate(Title,'&#xA;','')"/></dcvalue -->
                
                
                <xsl:for-each select="author">
                    <dcvalue element="contributor" qualifier="author"><xsl:value-of select="Lname"/>, <xsl:value-of select="Fname"/></dcvalue>        
                </xsl:for-each>
                

                <!-- If value of Adviser1 is not "NA" then record it-->
                <xsl:if test="not(Adviser1='NA')">
                    <dcvalue element="contributor" qualifier="advisor"><xsl:value-of select="Adviser1"/></dcvalue>
                </xsl:if>

                <!-- If a second advisor exists then record it-->
                <xsl:if test="Adviser2">
                    <dcvalue element="contributor" qualifier="none"><xsl:value-of select="Adviser2"/></dcvalue>
                </xsl:if>

                <!-- Number of pages -->
                <!-- If number of pages is greater than 0 -->
                <xsl:if test="Pages &gt; 0">
                    <dcvalue element="format" qualifier="extent"><xsl:value-of select="Pages"/> Pages</dcvalue>
                </xsl:if>
                
                <!-- Type field -->
                <dcvalue element="type" qualifier="none">Princeton University Senior Theses</dcvalue>
                
                <!-- If there is a Thesis Number then record it-->
                <xsl:if test="ThesisNo">
                    <dcvalue element="identifier" qualifier="other"><xsl:value-of select="ThesisNo"/></dcvalue>
                </xsl:if>

                <!-- If contains color or special media -->
                <xsl:if test="not(Color_x002F_Special_x0020_Media='0')">
                    <dcvalue element="format" qualifier="none">Contains color or special media</dcvalue>
                </xsl:if>

                <!-- Set issue date to the year of the thesis -->
                <dcvalue element="date" qualifier="issued"><xsl:value-of select="Year"/></dcvalue>
            </dublin_core>

        </saxon:output>

        <!-- Write the pu_schema.xml file -->
        <saxon:output
            href="{$outputfolder}/{$foldername}/{position()}/metadata_pu.xml">
            
            <dublin_core schema="pu">
                <!-- Princeton project grant number for charging if/when appropriate -->
                <dcvalue element="projectgrantnumber" qualifier="none">690-2143</dcvalue>
                
                <!-- Year student graduated -->
                <dcvalue element="date" qualifier="classyear"><xsl:value-of select="Year"/></dcvalue>
                
                <!-- Physical location of the thesis -->
                <dcvalue element="location">
                    <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                    This thesis can be viewed only at the <a href='http://www.princeton.edu/~mudd/'>Mudd Manuscript Library</a>. 
                    Contact <a href='mailto:mudd@princeton.edu'>mudd@princeton.edu</a> for more information or to order a copy.
                    <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
                </dcvalue>
                
                <!-- Academic department(s) for the thesis -->
                <xsl:apply-templates select="Dcode1|Dcode2" mode="dcode2name"/>
            </dublin_core>

        </saxon:output>
        
        <!-- Write collection identifiers to a file.  Collection identifiers will be passed to the ItemImport app during import. -->
        <saxon:output
            href="{$outputfolder}/{$foldername}/{position()}/collections.txt">
            
            <xsl:apply-templates select="Dcode1|Dcode2" mode="dcode2ark"/>
            
        </saxon:output>

    </xsl:template>

    <!-- Translate the department code into the department name -->
    <xsl:template match="Dcode1|Dcode2" mode="dcode2name">
        <dcvalue element="department" qualifier="none">
            <xsl:choose>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'AER'">Aeronautical Engineering</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ANT'">Anthropology</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ARC'">Architecture School</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'AAR'">Art and Archaeology</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'AST'">Astrophysical Sciences</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'BCH'">Biochemical Sciences</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'BIO'">Biology</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CHE'">Chemical and Biological Engineering</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CHM'">Chemistry</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CEE'">Civil and Environmental Engineering</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CEO'">Civil Engineering and Operations Research</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CLA'">Classics</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'COL'">Comparative Literature</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'COS'">Computer Science</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CRE'">Creative Writing Program</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EAS'">East Asian Studies</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EEB'">Ecology and Evolutionary Biology</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ECO'">Economics</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EEN'">Electrical Engineering</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EGI'">Engineering and Applied Science</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ENG'">English</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'FIT'">French and Italian</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'GEO'">Geosciences</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'GLL'">German</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'HIS'">History</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'IND'">Independent Concentration</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MAT'">Mathematics</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MEC'">Mechanical and Aerospace Engineering</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MED'">Medieval Studies</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MOL'">Modern Languages</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MBI'">Molecular Biology</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MUS'">Music</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'NES'">Near Eastern Studies</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ORF'">Operations Research and Financial Engineering</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ORS'">Oriental Studies</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'PHI'">Philosophy</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'PHY'">Physics</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'POL'">Politics</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'PSY'">Psychology</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'REL'">Religion</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'RLL'">Romance Languages and Literatures</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'SLL'">Slavic Languages and Literature</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'SOC'">Sociology</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'SPL'">Spanish and Portuguese Languages and Cultures</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'HUM'">Special Program in Humanities</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'STA'">Statistics</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'THE'">Theatre</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'WWS'">Woodrow Wilson School</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'NA'">NA</xsl:when>
                <xsl:otherwise>Unknown</xsl:otherwise>
            </xsl:choose>
        </dcvalue>
    </xsl:template>
    
    <!-- Translate the department code into the ARK for the corresponding DSpace collection -->
    <xsl:template match="Dcode1|Dcode2" mode="dcode2ark">
        <!-- First print a newline -->
        <xsl:text>&#xa;</xsl:text>
        <!-- Print the ARK for the corresponding department code -->
            <xsl:choose>
                <!-- Values for QA system 
                <xsl:when test="translate(., $smallcase, $uppercase) = 'AER'">88435/scr013t945q80r</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ANT'">88435/scr0102870v90x</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ARC'">88435/scr01v979v310w</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'AAR'">88435/scr01qj72p717x</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'AST'">88435/scr01ks65hc24q</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'BCH'">88435/scr01n583xv011</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'BIO'">88435/scr01g158bh337</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CHE'">88435/scr01bc386j24h</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CHM'">88435/scr016m311p33x</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CEE'">88435/scr012v23vt42h</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CEO'">88435/scr01z316q1621</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CLA'">88435/scr01tb09j569r</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'COL'">88435/scr01pk02c976v</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'COS'">88435/ktx34q7</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CRE'">88435/scr01js956f85b</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EAS'">88435/scr01f4752g761</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EEB'">88435/scr019c67wm85m</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ECO'">88435/scr015m60qr941</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EEN'">88435/scr011v53jx016</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EGI'">88435/scr01x346d4202</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ENG'">88435/scr01sb397828f</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'FIT'">88435/scr01nk322d37v</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'GEO'">88435/scr01hx11xf28m</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'GLL'">88435/kt89127</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'HIS'">88435/ktsb405</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'IND'">88435/scr01d504rk374</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MAT'">88435/scr018c97kq45z</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MEC'">88435/scr014m90dv53q</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MED'">88435/scr010v8380602</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MOL'">88435/scr01w37636801</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MBI'">88435/scr01rb68xb89j</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MUS'">88435/scr01mp48sc80w</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'NES'">88435/scr01gx41mh897</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ORF'">88435/scr01c534fn973</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ORS'">88435/scr017d278t05x</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'PHI'">88435/scr013n203z121</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'PHY'">88435/scr01zw12z532m</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'POL'">88435/scr01v405s9414</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'PSY'">88435/scr01qf85nb32s</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'REL'">88435/scr01kp78gg41w</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'RLL'">88435/scr01fx719m49k</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'SLL'">88435/scr01b5644r57f</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'SOC'">88435/scr016d56zw64q</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'SPL'">88435/scr012n49t172q</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'HUM'">88435/scr01xw42n7937</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'STA'">88435/scr01t722h884x</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'THE'">88435/scr01pg15bd931</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'WWS'">88435/scr01jq085k01v</xsl:when>
                -->
                <!-- Values for Production system -->
                <xsl:when test="translate(., $smallcase, $uppercase) = 'AER'">88435/dsp015m60qr96c</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ANT'">88435/dsp011v53jx03j</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ARC'">88435/dsp01x346d4232</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'AAR'">88435/dsp01sf268516n</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'AST'">88435/dsp01np1939243</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'BCH'">88435/xxxxxxxxxxxxxxxxxxxxxxxxscr01n583xv011</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'BIO'">88435/dsp01hx11xf31p</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CHE'">88435/dsp01d504rk39g</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CHM'">88435/dsp018c97kq479</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CEE'">88435/dsp014m90dv552</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CEO'">88435/dsp010v8380632</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CLA'">88435/dsp01w66343685</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'COL'">88435/dsp01rf55z7763</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'COS'">88435/dsp01mp48sc83w</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'CRE'">88435/dsp01gx41mh91n</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EAS'">88435/dsp01c534fn99f</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EEB'">88435/dsp017d278t078</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ECO'">88435/dsp013n203z151</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EEN'">88435/dsp0100000007x</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'EGI'">88435/dsp01v692t627b</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ENG'">88435/dsp01qf85nb35s</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'FIT'">88435/dsp01kp78gg437</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'GEO'">88435/dsp01fx719m510</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'GLL'">88435/dsp01b5644r59s</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'HIS'">88435/dsp016d56zw67q</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'IND'">88435/dsp012r36tx59n</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MAT'">88435/dsp01z029p4795</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MEC'">88435/dsp01t722h887x</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MED'">88435/dsp01pg15bd95c</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MOL'">88435/dsp01jq085k036</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MBI'">88435/dsp01dz010q11z</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'MUS'">88435/dsp019593tv19m</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'NES'">88435/dsp015h73pw11m</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ORF'">88435/dsp011r66j119j</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'ORS'">88435/dsp01x059c739h</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'PHI'">88435/dsp01s7526c478</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'PHY'">88435/dsp01ng451h55q</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'POL'">88435/dsp01hq37vn649</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'PSY'">88435/dsp01cz30ps722</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'REL'">88435/dsp018910jt63r</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'RLL'">88435/dsp014j03cz716</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'SLL'">88435/dsp010r967379h</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'SOC'">88435/dsp01w0892999g</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'SPL'">88435/dsp01r781wg073</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'HUM'">88435/dsp01mg74qm166</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'STA'">88435/dsp01gq67jr24n</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'THE'">88435/dsp01c247ds15b</xsl:when>
                <xsl:when test="translate(., $smallcase, $uppercase) = 'WWS'">88435/dsp0179407x233</xsl:when>
                
                <xsl:when test="translate(., $smallcase, $uppercase) = 'NA'"></xsl:when>
                <xsl:otherwise>Unknown</xsl:otherwise>
            </xsl:choose>   
    </xsl:template>

</xsl:stylesheet>