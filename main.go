package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"time"

	tb "gopkg.in/telebot.v3"
)

func main() {
	pref := tb.Settings{
		Token:  os.Getenv("TG_TOKEN"),
		Poller: &tb.LongPoller{Timeout: 10 * time.Second},
	}

	b, err := tb.NewBot(pref)
	if err != nil {
		log.Fatalln("Telegram", err)
		return
	}

	b.Handle(tb.OnChatJoinRequest, func(c tb.Context) error {
		req := c.ChatJoinRequest()

		path := filepath.Join(os.Getenv("MESSAGES_FOLDER"), fmt.Sprintf("%d.txt", req.Chat.ID))
		content, err := ioutil.ReadFile(path)
		if err != nil {
			log.Println("Can't load welcome message", path, err)
			return nil
		}
		_, err = b.Send(req.Sender, string(content), tb.ModeHTML)
		if err != nil {
			log.Println("Can't send welcome message", err)
		}
		
		err := b.ApproveChatJoinRequest(req.Chat, req.Sender)
		if err != nil {
			log.Println("Can't approve chat join request:", err)
		}

		return nil
	})

	log.Println("Starting bot")
	b.Start()
}
