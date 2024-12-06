import React from 'react'
import Navbar from './Navbar'
import SongGrid from './SongGrid'
import Sidebar from './SideBar'

const DisplayHome = () => {
  return (
    <>
    <div className="flex justify-center items-center">
      <button className="px-4 py-2 m-5 bg-[#BABEB8] text-[#092D3A] rounded">
        Album
      </button>
      <button className="px-4 py-2 m-5 bg-[#BABEB8] text-[#092D3A] rounded">
        Music
      </button>
    </div>
    <div>
      <SongGrid/>
    </div>
    </>
  )
}

export default DisplayHome