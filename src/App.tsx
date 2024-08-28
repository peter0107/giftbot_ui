import { useState } from 'react'
import { Button } from "./styles/button"
import { Input } from "./styles/input"
import './styles/index.css';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "./styles/card"
import { AlertCircle, CheckCircle2, Sparkles } from 'lucide-react'

export default function Component({group_id}: any) {
  const [answer, setAnswer] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [nickName, setNickName]= useState('')
  const [feedback, setFeedback] = useState('')
  const [isCorrect, setIsCorrect] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isFinalSubmitted, setIsFinalSubmitted] = useState(false)

  const correctAnswer = "비트코인"

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (answer.toLowerCase() === correctAnswer.toLowerCase()) {
      setFeedback("정답입니다!")
      setIsCorrect(true)
      setIsSubmitted(true)
    } else {
      setFeedback("틀렸습니다. 다시 시도해주세요.")
      setIsCorrect(false)
    }
  }

  const handleFinalSubmit = async () => {

    //api로 보낼 전번
    const payload= {
      phoneNumber,
      nickName,
      group_id: group_id
    }

    try{
      const response=await fetch("https://telegram-giftbot.com/api/participants",{
        method: 'POST',
        headers:{
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if(response.ok){
        setFeedback("참가가 완료되었습니다.")
        setIsFinalSubmitted(true)
      } else{
        setFeedback("참가 요청에 실패했습니다. 다시 시도해주세요.")
        setIsFinalSubmitted(false)
      }
    } catch(error){
      console.error("Error submitting:",error)
      setFeedback("서버 오류가 발생했습니다. 나중에 다시 시도해주세요.")
      setIsFinalSubmitted(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
      <Card className="w-full max-w-md mx-auto overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-6 h-6" />
              <span className="font-semibold">Have fun</span>
            </div>
            <CardTitle className="text-xl font-bold">Application</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="mt-6 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="question" className="block text-sm font-medium text-gray-700">
                블록체인 기술을 기반으로 만들어진 세계 최초 온라인 암호화폐는?
              </label>
              <Input
                id="question"
                type="text"
                placeholder="한글로 입력하세요"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                className="transition-all duration-200 focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            <Button type="submit" className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 transition-all duration-200">
              제출
            </Button>
          </form>
          {feedback && (
            <div className={`flex items-center space-x-2 ${isCorrect ? 'text-green-600' : 'text-red-600'} transition-all duration-200`}>
              {isCorrect ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
              <span>{feedback}</span>
            </div>
          )}
          {isSubmitted && !isFinalSubmitted && (
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                전화번호:
              </label>
              <Input
                id="phone"
                type="tel"
                placeholder="전화번호를 입력하세요(ex.01012345678)"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="transition-all duration-200 focus:ring-2 focus:ring-purple-500"
                required
              />
              <label htmlFor="nickname" className="block text-sm font-medium text-gray-700">
                닉네임:
              </label>
              <Input
                id="nickname"
                type="text"
                placeholder="닉네임을 입력하세요"
                value={nickName}
                onChange={(e)=>setNickName(e.target.value)}
                className='transition-all duration-200 focus:ring-2 focus:ring-purple-500'
                required

              />
              <Button 
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 transition-all duration-200"
                onClick={handleFinalSubmit}
                disabled={!phoneNumber || !nickName } //전화번호와 닉네임이 모두 입력되었을 때만 submit 가능
              >
                참가 완료
              </Button>
            </div>
          )}
        </CardContent>
        <CardFooter className="bg-gray-50 text-center text-sm text-gray-500">
          INF CryptoLab
        </CardFooter>
      </Card>
    </div>
  )
}