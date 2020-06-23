package com.example.demo;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

@RestController
public class HelloWorldController {

    @GetMapping("/")
    public String helloWorld()
    {
        return "Hello World";
    }

}