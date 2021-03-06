" vim: set fdm=marker et ts=4 sw=4 sts=4:

" Init: {{{1
function! pandoc#keyboard#Init()
    " set up defaults {{{2
    " Enabled submodules {{{3
    if !exists("g:pandoc#keyboard#enabled_submodules")
        let g:pandoc#keyboard#enabled_submodules = ["lists", "sections", "styles", "references"]
    endif
    " Use display motions when using soft wrapping {{{3
    if !exists("g:pandoc#keyboard#display_motions")
        let g:pandoc#keyboard#display_motions = 1
    endif
    " Use default mappings? {{{3
    if !exists("g:pandoc#keyboard#use_default_mappings")
        let g:pandoc#keyboard#use_default_mappings = 1
    endif

    " Display_Motion: {{{2
    if g:pandoc#keyboard#display_motions == 1
        " these are not useful when using the hard wraps mode.
        if exists("g:pandoc#formatting#mode") && stridx(g:pandoc#formatting#mode, "s") > -1
            " Remappings that make j and k behave properly with soft wrapping.
            nnoremap <buffer> j gj
            nnoremap <buffer> k gk
            vnoremap <buffer> j gj
            vnoremap <buffer> k gk
        endif
    endif "}}}2
  
    " Submodules: {{{2
    for module in g:pandoc#keyboard#enabled_submodules
        exe "call pandoc#keyboard#".module."#Init()"
    endfor
    "}}}2
endfunction
"}}}1

" Functions: {{{1
function! pandoc#keyboard#MovetoLine(line)
    if a:line > 0
        call cursor(a:line, 1)
    endif
    normal ^
endfunction
" }}}1

