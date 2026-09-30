# Print C function definitions from a source file, unchanged.
#   awk -v fn=NAME -f extract.awk file.c              one function
#   awk -v fn=FIRST -v to=LAST -f extract.awk file.c  FIRST through LAST, with
#                                                     everything between them
# A definition starts at the first line in column 0 that names the function followed
# by "(" and does not end in ";" (not a prototype), and ends at the next line that
# starts with "}". Exits nonzero if a name is not found, so a renamed or removed
# function fails the test build instead of silently testing nothing.
function starts(name) {
	return $0 ~ ("^[A-Za-z_].*[^A-Za-z0-9_]" name "[ \t]*\\(") && $0 !~ /;[ \t]*$/
}
BEGIN { if (to == "") to = fn }
!printing && starts(fn) {
	printing = 1; found = 1
	printf "#line %d \"%s\"\n", FNR, FILENAME
}
printing && starts(to) { last = 1 }
printing { print; if (last && $0 ~ /^}/) { done = 1; exit } }
END {
	if (!found) { print "extract.awk: " fn " not found in " FILENAME > "/dev/stderr"; exit 1 }
	if (!done) { print "extract.awk: end of " to " not found in " FILENAME > "/dev/stderr"; exit 1 }
}
