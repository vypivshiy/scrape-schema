package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os/exec"
)

type Book struct {
	Available bool     `json:"available"`
	Image     string   `json:"image"`
	Name      string   `json:"name"`
	Price     float32  `json:"price"`
	Rating    byte     `json:"rating"`
	Url       string   `json:"url"`
	Urls      []string `json:"urls"`
}

type MainPage struct {
	Books []Book `json:"books"`
}

func main() {
	// Send HTTP request and read response body
	response, err := http.Get("https://books.toscrape.com/catalogue/page-3.html")
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	defer response.Body.Close()

	body, err := ioutil.ReadAll(response.Body)
	if err != nil {
		panic(err)
	}
    // send html body to scrape-schema script
	cmd := exec.Command("python3", "stdin_adapter.py")
	cmd.Stdin = bytes.NewBuffer(body)
	output, err := cmd.Output()
	if err != nil {
		panic(err)
	}

	var data MainPage

	err = json.Unmarshal(output, &data)
	if err != nil {
		panic(err)
	}
    fmt.Println(data.Books[0])
    fmt.Println(data.Books[1])
}
