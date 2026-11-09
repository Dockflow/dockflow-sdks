"""Add what Maven Central requires to the generated pom: sources, javadoc, GPG signatures and the Central upload.
Usage: python3 maven_release.py <pom.xml>
"""
import sys
import xml.etree.ElementTree as ET

NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)
q = lambda tag: f"{{{NS}}}{tag}"  # noqa: E731

PLUGINS = {
    "maven-source-plugin": ("org.apache.maven.plugins", "3.3.1",
        "<executions><execution><id>attach-sources</id><goals><goal>jar-no-fork</goal></goals></execution></executions>"),
    "maven-javadoc-plugin": ("org.apache.maven.plugins", "3.12.0",
        "<configuration><doclint>none</doclint><failOnError>false</failOnError></configuration>"
        "<executions><execution><id>attach-javadocs</id><goals><goal>jar</goal></goals></execution></executions>"),
    "maven-gpg-plugin": ("org.apache.maven.plugins", "3.2.8",
        "<configuration><gpgArguments><arg>--pinentry-mode</arg><arg>loopback</arg></gpgArguments></configuration>"
        "<executions><execution><id>sign-artifacts</id><phase>verify</phase><goals><goal>sign</goal></goals></execution></executions>"),
    "central-publishing-maven-plugin": ("org.sonatype.central", "0.12.0",
        "<extensions>true</extensions><configuration><publishingServerId>central</publishingServerId>"
        "<autoPublish>true</autoPublish><waitUntil>published</waitUntil></configuration>"),
}

pom = sys.argv[1]
tree = ET.parse(pom)
project = tree.getroot()
build = project.find(q("build"))
if build is None:
    build = ET.SubElement(project, q("build"))
plugins = build.find(q("plugins"))
if plugins is None:
    plugins = ET.SubElement(build, q("plugins"))

for artifact, (group, version, body) in PLUGINS.items():
    for existing in plugins.findall(q("plugin")):
        if existing.findtext(q("artifactId")) == artifact:
            plugins.remove(existing)
    plugin = ET.fromstring(
        f'<plugin xmlns="{NS}"><groupId>{group}</groupId><artifactId>{artifact}</artifactId>'
        f"<version>{version}</version>{body}</plugin>")
    plugins.append(plugin)

tree.write(pom, xml_declaration=True, encoding="UTF-8")
print(f"maven_release: {len(PLUGINS)} release plugins set in {pom}")
