# test/test.asm

imports  

```asm
global _start

section .data
    msg db "hello world", 0xa
```

## hello world program

hello world program  

```asm
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
```
# test/test.bas

imports  

```bas
Option Explicit
```

## hello world program

hello world program  

```bas
Sub Main()
    Print "hello world"
End Sub
```
# test/test.c

```c
// imports
#include <stdio.h>
```

## hello world program

 * hello world program   
 *  

```c
int main(void)
{
    printf("hello world");
    return 0;
}
```
# test/test.cc

```cc
// imports
#include <iostream>
```

## hello world program

 * hello world program   
 *  

```cc
int main() {
    std::cout << "hello world" << std::endl;
    return 0;
}
```
# test/test.cls

imports  

```cls
\NeedsTeXFormat{LaTeX2e}
```

## hello world program

hello world program  

```cls
\ProvidesClass{test}
```
# test/test.cpp

```cpp
// imports
#include <iostream>
```

## hello world program

 * hello world program   
 *  

```cpp
int main() {
    std::cout << "hello world" << std::endl;
    return 0;
}
```
# test/test.cs

```cs
// imports
using System;
```

## hello world program

 * hello world program   
 *  

```cs
class Program {
    static void Main() {
        Console.WriteLine("hello world");
    }
}
```
# test/test.cxx

```cxx
// imports
#include <iostream>
```

## hello world program

 * hello world program   
 *  

```cxx
int main() {
    std::cout << "hello world" << std::endl;
    return 0;
}
```
# test/test.d

```d
// imports
import std.stdio;
```

## hello world program

 * hello world program   
 *  

```d
void main() {
    writeln("hello world");
}
```
# test/test.dart

```dart
// imports
import 'dart:io';
```

## hello world program

 * hello world program   
 *  

```dart
void main() {
    print('hello world');
}
```
# test/test.erlang

imports  

```erlang
-module(test).
```

## hello world program

hello world program  

```erlang
-export([hello_world/0]).

hello_world() ->
    io:format("hello world~n").
```
# test/test.fs

```fs
// imports
open System
```

## hello world program

 * hello world program   
 *  

```fs
[<EntryPoint>]
let main argv =
    printfn "hello world"
    0
```
# test/test.go

```go
// imports
package main

import "fmt"
```

## hello world program

 * hello world program   
 *  

```go
func main() {
    fmt.Println("hello world")
}
```
# test/test.h

```h
// imports
#include <stdio.h>
```

## hello world program

 * hello world program   
 *  

```h
#ifndef TEST_H
#define TEST_H

void hello_world(void);

#endif
```
# test/test.hh

```hh
// imports
#include <string>
```

## hello world program

 * hello world program   
 *  

```hh
#ifndef TEST_HH
#define TEST_HH

std::string hello_world();

#endif
```
# test/test.hpp

```hpp
// imports
#include <string>
```

## hello world program

 * hello world program   
 *  

```hpp
#ifndef TEST_HPP
#define TEST_HPP

std::string hello_world();

#endif
```
# test/test.hs

```hs
-- imports
module Test where
```

## hello world program

 * hello world program   
 *  

```hs
main :: IO ()
main = putStrLn "hello world"
```
# test/test.htm

imports  

```htm
<!DOCTYPE html>
```

## hello world program

 * hello world program   
 *  

```htm
<html>
<body>
<h1>hello world</h1>
</body>
</html>
```
# test/test.html

imports  

```html
<!DOCTYPE html>
```

## hello world program

 * hello world program   
 *  

```html
<html>
<body>
<h1>hello world</h1>
</body>
</html>
```
# test/test.inc

```inc
// imports
program Test;
```

## hello world program

 * hello world program   
 *  

```inc
begin
    writeln('hello world');
end.
```
# test/test.java

```java
// imports
import java.util.*;
```

## hello world program

 * hello world program   
 *  

```java
public class Test {
    public static void main(String[] args) {
        System.out.println("hello world");
    }
}
```
# test/test.js

```js
// imports
import fs from "fs";
```

## hello world program

 * hello world program   
 *  

```js
console.log("hello world");
```
# test/test.jsx

```jsx
// imports
import React from "react";
```

## hello world program

 * hello world program   
 *  

```jsx
const App = () => <h1>hello world</h1>;

export default App;
```
# test/test.kt

```kt
// imports
import kotlin.io.*
```

## hello world program

 * hello world program   
 *  

```kt
fun main() {
    println("hello world")
}
```
# test/test.kts

```kts
// imports
import kotlin.io.*
```

## hello world program

 * hello world program   
 *  

```kts
println("hello world")
```
# test/test.lua

```lua
-- imports
local io = require("io")
```

## hello world program

 * hello world program   
 *  

```lua
print("hello world")
```
# test/test.m

```m
% imports
clc;
```

## hello world program

 * hello world program   
 *  

```m
disp("hello world");
```
# test/test.mm

```mm
// imports
#import <Foundation/Foundation.h>
```

## hello world program

 * hello world program   
 *  

```mm
int main() {
    @autoreleasepool {
        NSLog(@"hello world");
    }
    return 0;
}
```
# test/test.pas

```pas
// imports
program Test;
```

## hello world program

 * hello world program   
 *  

```pas
begin
    writeln('hello world');
end.
```
# test/test.php

```php
// imports
<?php
```

## hello world program

 * hello world program   
 *  

```php
echo "hello world";
```
# test/test.pp

```pp
// imports
program Test;
```

## hello world program

 * hello world program   
 *  

```pp
begin
    writeln('hello world');
end.
```
# test/test.py

```py
# imports
import sys
```

## hello world program

 * hello world program   
 *  

```py
print("hello world")
```
# test/test.pyi

```pyi
# imports
import sys
```

## hello world program

 * hello world program   
 *  

```pyi
def hello_world() -> None: ...
```
# test/test.pyw

```pyw
# imports
import sys
```

## hello world program

 * hello world program   
 *  

```pyw
print("hello world")
```
# test/test.rs

```rs
// imports
use std::io;
```

## hello world program

 * hello world program   
 *  

```rs
fn main() {
    println!("hello world");
}
```
# test/test.s

imports  

```s
global _start

section .data
    msg db "hello world", 0xa
```

## hello world program

hello world program  

```s
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
```
# test/test.scala

```scala
// imports
import scala.io.StdIn
```

## hello world program

 * hello world program   
 *  

```scala
object Test extends App {
    println("hello world")
}
```
# test/test.sty

imports  

```sty
\NeedsTeXFormat{LaTeX2e}
```

## hello world program

hello world program  

```sty
\ProvidesPackage{test}
```
# test/test.swift

```swift
// imports
import Foundation
```

## hello world program

 * hello world program   
 *  

```swift
print("hello world")
```
# test/test.tex

imports  

```tex
\documentclass{article}
```

## hello world program

hello world program  

```tex
\begin{document}
hello world
\end{document}
```
# test/test.ts

```ts
// imports
console.log("import")
```

## hello world program

 * hello world program   
 *  

```ts
console.log("hello world");
```
# test/test.tsx

```tsx
// imports
import React from "react";
```

## hello world program

 * hello world program   
 *  

```tsx
const App: React.FC = () => <h1>hello world</h1>;

export default App;
```
# test/test.vb

imports  

```vb
Imports System
```

## hello world program

hello world program  

```vb
Module Test
    Sub Main()
        Console.WriteLine("hello world")
    End Sub
End Module
```
# test/test.vbs

imports  

```vbs
Option Explicit
```

## hello world program

hello world program  

```vbs
WScript.Echo "hello world"
```
# test/test.xhtml

imports  

```xhtml
<?xml version="1.0"?>
```

## hello world program

 * hello world program   
 *  

```xhtml
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>hello world</title></head>
<body>hello world</body>
</html>
```
# test/test.xml

imports  

```xml
<?xml version="1.0"?>
```

## hello world program

 * hello world program   
 *  

```xml
<greeting>hello world</greeting>
```
# test/test.zig

imports  

```zig
const std = @import("std");
```

## hello world program

```zig
/* 
 * hello world program 
 * */

pub fn main() void {
    std.debug.print("hello world\n", .{});
}
```
