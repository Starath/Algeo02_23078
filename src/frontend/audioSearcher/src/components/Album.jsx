import React from 'react'
import { Route, Routes } from 'react-router-dom'
import DisplayHome from './DisplayHome'

const Album = () => {
  return (
    <div className='w-[100%] m-2 px-6 pt-4 rounded bg-[#092D3A] text-white overflow-auto lg:w-[75%] lg:ml-0'>
        <Routes>
            <Route path='/' element={<DisplayHome/>}/>
        </Routes>
    </div>
  )
}

export default Album