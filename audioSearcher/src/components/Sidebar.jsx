import React from 'react'

const Sidebar = () => {
  return (
    <div className='w-[25%] h-[100%] p-2 flex-col gap-2 text-white lg-flex'>
        <div className='bg-[#19191a] h-[100%] rounded flex flex-col justify-around'>
            <div className='bg-white h-screen  flex justify-center items-center rounded m-5'></div>
            <div class="flex justify-center items-center p-8">
                <button class="px-4 py-2 bg-[#3054d9] text-white rounded">Upload</button>
            </div>

            <div class="flex justify-center items-center p-2">
                <button class="px-4 py-2 bg-[#3054d9] text-white rounded">Audios</button>
            </div>
            <div class="flex justify-center items-center p-2">
                <button class="px-4 py-2 bg-[#3054d9] text-white rounded">Pictures</button>
            </div>
            <div class="flex justify-center items-center p-2">
                <button class="px-4 py-2 bg-[#3054d9] text-white rounded">Mapper</button>
            </div>

            
        </div>
    </div>
  )
}

export default Sidebar