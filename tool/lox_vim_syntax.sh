#!/usr/bin/env bash

# sets up lox syntax higlighting for vim

set -e
mkdir -p ~/.vim/ftdetect
mkdir -p ~/.vim/syntax

cat > ~/.vim/syntax/lox.vim << 'EOF'
" Bssic syntax highlighting for Lox language

" --- Keywords ---
syntax keyword loxKeyword and class else false fun for if nil or print return super this true var while break

" --- Literals ---
syntax match loxNumber "\<[0-9]\+\>"
syntax region loxString start=/"/ end=/"/

" --- Comments ---
syntax match loxComment "//.*"
syntax region loxMultilineComment start="/\*" end="\*/"

" --- Highlight linking ---
highlight link loxKeyword Keyword
highlight link loxNumber Number
highlight link loxString String
highlight link loxComment Comment
highlight link loxMultilineComment Comment
EOF

cat > ~/.vim/ftdetect/lox.vim << 'EOF'
" Detect .lox files and set filetype
au BufRead,BufNewFile *.lox set filetype=lox
EOF
