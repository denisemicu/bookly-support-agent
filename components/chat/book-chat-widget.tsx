"use client"

import { useState } from "react"
import {
  BookOpen,
  Sparkles,
  X,
  MessageCircle,
  Loader2,
  Wrench,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Conversation,
  ConversationContent,
  ConversationEmptyState,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation"
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message"
import {
  PromptInput,
  type PromptInputMessage,
  PromptInputBody,
  PromptInputTextarea,
  PromptInputFooter,
  PromptInputSubmit,
} from "@/components/ai-elements/prompt-input"

type ChatRole = "user" | "assistant"

type AgentTrace = {
  intent?: string
  action?: string
  tool_called?: string | null
}

type ChatMessage = {
  id: string
  role: ChatRole
  text: string
  trace?: AgentTrace
}

type AgentResponse = {
  response: string
  intent?: string
  action?: string
  tool_called?: string | null
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000"
const GREETING: ChatMessage = {
  id: "greeting",
  role: "assistant",
  text: "Hello, and welcome to Bookly. I'm Pip, here to help with order tracking and returns. How can I help you today?",
}

function formatTraceValue(value?: string | null) {
  if (!value) return "—"

  return value.replaceAll("_", " ")
}

export function BookChatWidget() {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)

  async function addUserMessage(text: string) {
    const trimmed = text.trim()

    if (!trimmed || isLoading) return

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      text: trimmed,
    }

    // Send only prior conversational messages as backend history.
    // The backend uses this for multi-turn memory and workflow state.
    const history = messages.map((message) => ({
      role: message.role,
      content: message.text,
    }))

    setMessages((previousMessages) => [...previousMessages, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmed,
          history,
        }),
      })

      if (!response.ok) {
        throw new Error("The Bookly support service could not be reached.")
      }

      const data: AgentResponse = await response.json()

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: data.response,
        trace: {
          intent: data.intent,
          action: data.action,
          tool_called: data.tool_called,
        },
      }

      setMessages((previousMessages) => [...previousMessages, assistantMessage])
    } catch (error) {
      console.error(error)

      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: "I’m sorry, I’m having trouble connecting to Bookly support right now. Please try again in a moment.",
        trace: {
          intent: "error",
          action: "backend_connection_failed",
          tool_called: null,
        },
      }

      setMessages((previousMessages) => [...previousMessages, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  function handleSubmit(message: PromptInputMessage) {
    addUserMessage(message.text ?? "")
  }

  const allMessages = [GREETING, ...messages]

  return (
    <>
      <Button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-label={open ? "Close the Bookly assistant" : "Open the Bookly assistant"}
        className={cn(
          "fixed bottom-5 right-5 z-50 size-14 rounded-full bg-primary text-primary-foreground shadow-xl",
          "transition-transform hover:scale-105 hover:bg-primary/90 [&_svg]:size-6",
        )}
      >
        {open ? <X /> : <MessageCircle />}
      </Button>

      <div
        className={cn(
          "fixed bottom-24 right-5 z-50 flex w-[min(26rem,calc(100vw-2.5rem))] flex-col overflow-hidden rounded-3xl border border-border bg-card shadow-2xl",
          "h-[min(34rem,calc(100vh-8rem))] origin-bottom-right transition-all duration-200",
          open
            ? "pointer-events-auto translate-y-0 scale-100 opacity-100"
            : "pointer-events-none translate-y-3 scale-95 opacity-0",
        )}
        role="dialog"
        aria-label="Bookly support assistant"
        aria-hidden={!open}
      >
        <header className="flex items-center gap-3 border-b border-border bg-primary px-4 py-3 text-primary-foreground">
          <span className="flex size-9 items-center justify-center rounded-full bg-primary-foreground/15">
            <BookOpen className="size-5" />
          </span>

          <div className="flex-1">
            <p className="font-serif text-base font-semibold leading-tight">
              Pip from Bookly
            </p>
            <p className="flex items-center gap-1 text-xs text-primary-foreground/80">
              <Sparkles className="size-3" />
              Orders &amp; support
            </p>
          </div>
        </header>

        <Conversation className="flex-1 bg-background">
          <ConversationContent>
            {allMessages.length === 0 ? (
              <ConversationEmptyState
                icon={<BookOpen className="size-12" />}
                title="A quiet little nook"
                description="Ask Pip for help with an order or return."
              />
            ) : (
              <>
                {allMessages.map((message) => (
                  <Message from={message.role} key={message.id}>
                    <MessageContent>
                      <MessageResponse>{message.text}</MessageResponse>

                      {message.role === "assistant" && message.trace && (
                        <div className="mt-3 rounded-lg border border-border bg-muted/50 px-2.5 py-2 text-[11px] text-muted-foreground">
                          <div className="mb-1 flex items-center gap-1 font-medium text-foreground">
                            <Wrench className="size-3" />
                            Agent Trace
                          </div>

                          <div className="grid gap-0.5">
                            <p>
                              <span className="font-medium">Intent:</span>{" "}
                              {formatTraceValue(message.trace.intent)}
                            </p>
                            <p>
                              <span className="font-medium">Action:</span>{" "}
                              {formatTraceValue(message.trace.action)}
                            </p>
                            <p>
                              <span className="font-medium">Tool:</span>{" "}
                              {formatTraceValue(message.trace.tool_called)}
                            </p>
                          </div>
                        </div>
                      )}
                    </MessageContent>
                  </Message>
                ))}

                {isLoading && (
                  <Message from="assistant">
                    <MessageContent>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="size-4 animate-spin" />
                        Pip is checking that for you...
                      </div>
                    </MessageContent>
                  </Message>
                )}
              </>
            )}
          </ConversationContent>

          <ConversationScrollButton />
        </Conversation>

        <PromptInput
          onSubmit={handleSubmit}
          className="rounded-none border-0 border-t border-border"
        >
          <PromptInputBody>
            <PromptInputTextarea
              value={input}
              onChange={(event) => setInput(event.currentTarget.value)}
              placeholder="Ask about an order or return..."
              disabled={isLoading}
            />
          </PromptInputBody>

          <PromptInputFooter className="justify-end">
            <PromptInputSubmit
              status="ready"
              disabled={!input.trim() || isLoading}
            />
          </PromptInputFooter>
        </PromptInput>
      </div>
    </>
  )
}