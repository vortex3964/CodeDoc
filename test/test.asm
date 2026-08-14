;Doc code: includes
;includes
global _start

section .data
    msg db "hello world", 0xa

;Doc end

;Doc code : hello world program
; hello world program

section .text
_start:
    mov eax, 4
    mov ebx, 1
    mov ecx, msg
    mov edx, 12
    int 0x80
    mov eax, 1
    xor ebx, ebx
    int 0x80

;Doc end
