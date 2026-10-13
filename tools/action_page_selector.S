/* DQH1 Japanese Switch 1.0.0, experimental Action List page selector.
 * Called at CMenuBtlAction::OnRegister 0x251C28 instead of mov x2,x21.
 * Page2 is only selected on GetLevel(0) PAD bit20 and marker \0\x1fDQH2\x1f.
 * PAD bit20 is NOT confirmed as a physical button. Do not release as stable.
 */
 .text
 .p2align 2
 .global action_page_selector
 .type action_page_selector,%function
 .extern get_pad
 .extern get_level
 action_page_selector:
  stp x29, x30, [sp, #-0x40]!
  mov x29, sp
  stp x0, x1, [sp, #0x10]
  stp x3, x4, [sp, #0x20]
  mov x2, x21
  bl get_pad
  cbz x0, .Lreturn
  mov w1, wzr
  bl get_level
  tbz w0, #20, .Lreturn
  mov x9, x21
  mov w10, #240
 .Lfind_end:
  ldrb w11, [x9], #1
  cbz w11, .Lcheck_tag
  subs w10, w10, #1
  b.ne .Lfind_end
  b .Lreturn
 .Lcheck_tag:
  ldrb w11, [x9]
  cmp w11, #0x1f
  b.ne .Lreturn
  ldr w11, [x9, #1]
  movz w12, #0x5144
  movk w12, #0x3248, lsl #16
  cmp w11, w12
  b.ne .Lreturn
  ldrb w11, [x9, #5]
  cmp w11, #0x1f
  b.ne .Lreturn
  add x2, x9, #6
 .Lreturn:
  ldp x3, x4, [sp, #0x20]
  ldp x0, x1, [sp, #0x10]
  ldp x29, x30, [sp], #0x40
  ret
 .size action_page_selector, .-action_page_selector
