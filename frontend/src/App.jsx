import { useState, useEffect, useRef } from 'react'
import axios from 'axios' 


function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const containerRef = useRef(null)


  function sendQuery(e){
    e.preventDefault()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: input }])
    axios.post('http://127.0.0.1:5000/check', { message: input, context: messages })
      .then(res => {
        setMessages(prev => [...prev, { role: 'ai', content: res.data["response"] }])
      })
      .catch(err => {
        console.error(err)
        setMessages(prev => [...prev, { role: 'bot', content: 'Sorry, something went wrong!' }])
      })
  }

  useEffect(() => {
    containerRef.current?.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: "smooth"
    });
}, [messages]);
  return (
    <div className='bg-slate-800 text-slate-200 flex flex-col w-full h-screen items-center justify-center gap-4 p-4 '>
      <h1 className="text-3xl font-bold underline">
        Fake News Detection ChatBot
      </h1>
      <div className="w-[80%] h-[80%] border border-gray-300 rounded-lg p-4 flex flex-col ">
       <div 
            ref = {containerRef}
            className="flex flex-col gap-2 overflow-y-auto flex-1 pr-2 no-scrollbar"
            id="chat-container"
        >
            {messages.map((msg, index) => (
                <div
                    key={index}
                    className={`p-2 rounded-lg max-w-[70%] ${
                        msg.role === "user"
                            ? "bg-blue-500 text-white self-end"
                            : "bg-gray-200 text-gray-800 self-start"
                    }`}
                >
                    {msg.content}
                </div>
            ))}
        </div>

        {/* Input */}
        <form
            className="flex gap-2 mt-2"
            onSubmit={sendQuery}
        >
            <input
                type="text"
                placeholder="Type your message here..."
                className="flex-1 p-2 border rounded outline-none"
                value={input}
                onChange={(e) => setInput(e.target.value)}
            />
            <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded"
            >
                Send
            </button>
        </form>
    </div>
    </div>
  )
}

export default App
