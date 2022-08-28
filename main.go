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
		b.ApproveChatJoinRequest(req.Chat, req.Sender)

		path := filepath.Join(os.Getenv("MESSAGES_FOLDER"), fmt.Sprintf("%d.txt", req.Chat.ID))
		content, err := ioutil.ReadFile(path)
		if err != nil {
			log.Println("Can't load welcome message", path, err)
			return nil
		}
		b.Send(req.Sender, string(content), tb.ModeMarkdownV2)

		return nil
	})

	log.Println("Starting bot")
	b.Start()
}
