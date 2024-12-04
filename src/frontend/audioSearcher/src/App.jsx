import React from 'react'
import Navbar from './components/Navbar'
import Sidebar from './components/SideBar'
import Album from './components/Album'

const App = () => {
  return (
    <div className='h-screen bg-black'>
      <Navbar/>
      <div className='h-[90%] flex'>
        <Sidebar/>
        <Album/>
      </div>
      
    </div>
  )
}

export default App