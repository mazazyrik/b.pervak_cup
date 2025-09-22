import { FC } from 'react'

export const AuthRequiredOverlay: FC = () => {
  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75'>
      <div className='bg-white p-8 rounded-lg shadow-lg text-center'>
        <h2 className='text-2xl font-bold mb-4'>Требуется регистрация</h2>
        <p className='text-gray-700 mb-4'>
          Пожалуйста, пройдите регистрацию в нашем Telegram-боте, чтобы получить доступ к приложению.
        </p>
        <a
          href='https://t.me/b_pervak_cup_bot'
          target='_blank'
          rel='noopener noreferrer'
          className='inline-block bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded'
        >
          Перейти к боту
        </a>
      </div>
    </div>
  )
}
