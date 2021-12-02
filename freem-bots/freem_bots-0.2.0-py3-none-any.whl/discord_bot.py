import io
import logging
from typing import Awaitable, List, Optional
import discord
from discord.channel import VoiceChannel
import discord.ext.commands
import asyncio
import librosa
import soundfile
import wave

from freem_bots.asyncio_queue_log_handler import AsyncioQueueLogHandler
from freem_bots.configuration import Config
from freem_bots.random_provider import RandomProvider
from freem_bots.tts import TTS, TTSPause, TTSVoice, TTSVoiceline, TTSVoicelinePart, TTSVoicelineSpeed


class DiscordBot(discord.ext.commands.Bot):
	def __init__(self, configuration: Config) -> None:
		self._log_queue: 'asyncio.Queue[str]' = asyncio.Queue()
		self._logger = logging.getLogger('bot-discord')
		handler = AsyncioQueueLogHandler(self._log_queue)
		logging.root.addHandler(handler)
		super().__init__(command_prefix = '/', intents = self._intents)
		self._configuration = configuration
		self._random_provider: RandomProvider = RandomProvider()
		self.__load_opus()
		self._tts = TTS(self._configuration)
		self._init_tasks: List[Awaitable] = [self.__task_log_to_log_channel()]

	@property
	def _intents(self) -> discord.Intents:
		intents = discord.Intents.default()
		intents.members = True  # pylint: disable=assigning-non-slot
		return intents

	async def on_ready(self) -> None:
		''' Invoked when bot connects to Discord servers '''
		self._logger.info('Bot connected under %s', self.user.name)
		for waiting_task in self._init_tasks:
			self.loop.create_task(waiting_task)

	async def get_audio_for_text(self, text: str, voice: TTSVoice, username: str) -> bytes:
		''' Returns PCM for given lines '''
		username_lines = text.split('{}')
		message_voicelines: List[TTSVoicelinePart] = []
		for username_line in username_lines:
			message_voicelines.append(TTSVoicelinePart(voice, username_line.strip(), TTSVoicelineSpeed.NORMAL))
			message_voicelines.append(
				TTSVoicelinePart(voice, username.strip(), TTSVoicelineSpeed.SLOWER, prepended_pause = TTSPause.SHORT)
			)
		message_voicelines.pop()
		voiceline = TTSVoiceline(message_voicelines)
		return await self.get_voiceline_pcm(voiceline)

	async def get_audio_for_text_simple(self, text: str, voice: TTSVoice) -> bytes:
		''' Gets PCM for a simple string '''
		voiceline = TTSVoiceline([TTSVoicelinePart(voice, text)])
		return await self.get_voiceline_pcm(voiceline)

	async def get_voiceline_pcm(self, voiceline: TTSVoiceline) -> bytes:
		''' Gets PCM for voiceline content '''
		sample_rate = self.redis.get_int('bot_audio_processing_target_sample_rate', 96000)
		byts = await self._tts.get_audio_bytes(voiceline, sample_rate)
		return DiscordBot.get_pcm_from_bytes(byts)

	async def play_audiofile(self, filename: str, voice_channel: VoiceChannel) -> None:
		if '.' in filename:
			self._logger.warning('Refusing to resolve insecure path: filename=%s', filename)
			return
		full_path = f'audio_files/{filename}.wav'
		pcms = [self.get_pcm_from_file(full_path)]
		await self.play_pcms_in_voice_channel(voice_channel, pcms)

	def get_pcm_from_file(self, file) -> bytes:
		''' Gets PCM from a file '''
		(audio, original_sample_rate) = soundfile.read(file)
		target_samplerate = self.redis.get_int('bot_audio_processing_target_sample_rate', 96000)
		audio = librosa.resample(audio, orig_sr = original_sample_rate, target_sr = target_samplerate)
		soundfile.write(file, audio, target_samplerate)

		audio_file = wave.open(file, 'rb')
		num_frames: int = audio_file.getnframes()
		audio_raw: bytes = audio_file.readframes(num_frames)
		audio_file.close()

		return audio_raw

	@staticmethod
	def get_pcm_from_bytes(sound_bytes: bytes) -> bytes:
		''' Gets PCM from bytes '''
		with io.BytesIO(sound_bytes) as file:
			file.name = 'audio.wav'
			audio_file = wave.open(file, 'rb')
			num_frames: int = audio_file.getnframes()
			audio_raw: bytes = audio_file.readframes(num_frames)
			audio_file.close()

		return audio_raw

	def send_log_to_log_channel(self, message: str) -> None:
		self._log_queue.put_nowait(message)

	async def locate_user_in_voice_channel(self, target_user, guild) -> Optional[VoiceChannel]:
		voice_channels = [channel for channel in guild.channels if isinstance(channel, VoiceChannel)]
		located_channel = None
		for voice_channel in voice_channels:
			member_ids = [member.id for member in voice_channel.members]
			if target_user.id in member_ids:
				located_channel = voice_channel
				break
		return located_channel

	async def play_voiceline_in_voice_channel(
		self,
		voice_channel: VoiceChannel,
		voiceline: TTSVoiceline,
	) -> None:
		byts = await self._tts.get_audio_bytes(voiceline)
		pcms = [DiscordBot.get_pcm_from_bytes(byts)]
		await self.play_pcms_in_voice_channel(voice_channel, pcms)

	async def play_pcms_in_voice_channel(self, voice_channel: VoiceChannel, pcms) -> None:
		''' Plays a collection of PCMs in a voice channel '''
		# else, remove self, connect to voice channel, play audio, disconnect
		voice_client: discord.VoiceClient = await voice_channel.connect()
		try:
			pcm = []
			for pcm_ in pcms:
				pcm += pcm_
			pcm_bytes = bytes(pcm)
			audio_stream = io.BytesIO(pcm_bytes)
			audio_source = discord.PCMAudio(audio_stream)
			self._logger.debug('Starting playing')
			voice_client.play(audio_source)
			while voice_client.is_playing():
				await asyncio.sleep(0.1)
			self._logger.debug('Done playing')
			await voice_client.disconnect()
		except Exception:
			await voice_client.disconnect()
			raise

	async def sync_commands(self) -> None:
		return await super().sync_commands()

	async def _get_user_by_uid(self, guild: str, user_id: int) -> discord.Member:
		try:
			target_user_id = user_id
			# find the guild
			target_guilds = [i for i in self.guilds if i.name.lower() == guild.lower()]
			if len(target_guilds) == 0:
				self._logger.fatal('Unable to find %s guild', guild)
				return None
			target_guild = target_guilds[0]
			# get user
			members = [member for member in target_guild.members if member.id == target_user_id]
			if len(members) == 0:
				self._logger.error('Unable to find user in %s', guild)
				return None

			target_user = members[0]
			return target_user
		except discord.DiscordException:
			return None

	def __load_opus(self) -> None:
		if not discord.opus.is_loaded():
			discord.opus._load_default()  # pylint: disable=protected-access
		if not discord.opus.is_loaded():
			raise Exception('Unable to load OPUS audio library')

	async def __task_log_to_log_channel(self) -> None:
		log_channel_id = self._configuration.log_channel_id
		if log_channel_id is None:
			self._logger.warning("Won't log to discord, no log channel configured")
			while not self.is_closed():
				await self._log_queue.get()
				await asyncio.sleep(0.05)
			return
		log_channel = self.get_channel(log_channel_id)
		while not self.is_closed():
			while not self._log_queue.empty():
				message: str = await self._log_queue.get()
				try:
					message = message.replace('`', '\\`')
					message = f'`{message}`'
					await log_channel.send(message)
				except discord.DiscordException:
					await asyncio.sleep(5.0)  # probably hit rate limiting, if discord disconnect, loop will stop anyway
			await asyncio.sleep(0.05)
