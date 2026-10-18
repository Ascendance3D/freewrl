import re

with open("freex3d/src/lib/input/EAI_C_CommonFunctions.c", "r") as f:
    content = f.read()

# Replace the block
old_block = """\t\t\t\tif (!mfstringtmp) {
\t\t\t\t\tlexer_forceStringCleanup(parser->lexer);
\t\t\t\t\tparser->parsingX3DfromXML = oldXMLflag;
\t\t\t\t\treturn;
\t\t\t\t}"""

new_block = """\t\t\tif (!mfstringtmp) {
\t\t\t\tlexer_forceStringCleanup(parser->lexer);
\t\t\t\tparser->parsingX3DfromXML = oldXMLflag;
\t\t\t\treturn;
\t\t\t}"""

content = content.replace(old_block, new_block)

with open("freex3d/src/lib/input/EAI_C_CommonFunctions.c", "w") as f:
    f.write(content)
