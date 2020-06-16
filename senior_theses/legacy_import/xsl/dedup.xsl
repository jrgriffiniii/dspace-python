<?xml version="1.0" encoding="UTF-8"?>
<!-- 
    The data extracted from the Access database has one entry per author.
     A senior theses can have more than one auther, resulting in multiple entries.
     This stylesheet should be used to merge such entries into a single thesis
     with multiple authors. 

    Author:  Mark Ratliff
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>

    <!-- Do not preserve whitespace or new lines from XML file. -->
    <xsl:strip-space elements="*"/>
    
    <!-- Generate a hashtable of Title elements with the capitalized title text as the key -->
    <xsl:key name="TitleList" match="/dataroot/Theses/Title" use="translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>

    <xsl:template match="/">
        <dataroot>
            <xsl:apply-templates select="dataroot/Theses"/>
        </dataroot>
    </xsl:template>

    <!-- Process each Theses -->
    <xsl:template match="/dataroot/Theses">

        <!-- If this is the first thesis with the given Title, then process it.
             Perform case insensitive match on the title.
          -->
        <xsl:if test="generate-id(Title)=generate-id(key('TitleList',translate(Title, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))[1])">
            <Theses>
                <!-- Copy all nodes except for the author names -->
                <xsl:copy-of select="*[not(name()='Lname') and not(name()='Fname')]"/>

                <!-- Wrap each author name in a new <author> element -->
                <xsl:for-each select="key('TitleList', translate(Title, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))">
                    <author>
                        <Lname><xsl:value-of select="../Lname"/></Lname>
                        <Fname><xsl:value-of select="../Fname"/></Fname>
                    </author>
                </xsl:for-each>
            </Theses>
        </xsl:if>

    </xsl:template>

</xsl:stylesheet>