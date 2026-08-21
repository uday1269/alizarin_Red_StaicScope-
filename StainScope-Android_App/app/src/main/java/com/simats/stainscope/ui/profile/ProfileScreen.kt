package com.simats.stainscope.ui.profile

import androidx.compose.animation.*
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Logout
import androidx.compose.material.icons.automirrored.filled.OpenInNew
import androidx.compose.material.icons.automirrored.outlined.CompareArrows
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.simats.stainscope.ui.components.StainScopeTextField
import com.simats.stainscope.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    onNavigateToDashboard: () -> Unit,
    onNavigateToAnalysis: () -> Unit,
    onNavigateToCompare: () -> Unit,
    onNavigateToReports: () -> Unit,
    onNavigateToResults: (String) -> Unit,
    onNavigateBack: () -> Unit,
    onSignOut: () -> Unit,
    viewModel: ProfileViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var visible by remember { mutableStateOf(false) }
    var showAddNoteDialog by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        visible = true
        viewModel.loadProfileAndNotes()
        viewModel.clearOldRecycleBinItems()
    }

    if (uiState.isEditingProfile) {
        EditProfileDialog(
            uiState = uiState,
            onDismiss = { viewModel.setEditingProfile(false) },
            onSave = viewModel::updateProfile
        )
    }

    if (showAddNoteDialog) {
        AddNoteDialog(
            onDismiss = { showAddNoteDialog = false },
            onAdd = { title, content ->
                viewModel.addNote(title, content)
                showAddNoteDialog = false
            }
        )
    }

    Scaffold(
        topBar = {
            Column(modifier = Modifier.background(MaterialTheme.colorScheme.surface)) {
                TopAppBar(
                    title = { 
                        Text(
                            "Researcher Profile", 
                            fontWeight = FontWeight.Black, 
                            fontSize = 22.sp
                        ) 
                    },
                    navigationIcon = {
                        IconButton(onClick = onNavigateBack) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack, 
                                contentDescription = "Back"
                            )
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.surface,
                        titleContentColor = MaterialTheme.colorScheme.onSurface,
                        navigationIconContentColor = MaterialTheme.colorScheme.onSurface,
                        actionIconContentColor = MaterialTheme.colorScheme.onSurface
                    )
                )
                
                ScrollableTabRow(
                    selectedTabIndex = 4,
                    containerColor = MaterialTheme.colorScheme.surface,
                    contentColor = PrimaryMaroon,
                    edgePadding = 16.dp,
                    divider = {},
                    indicator = { tabPositions ->
                        if (tabPositions.size > 4) {
                            TabRowDefaults.SecondaryIndicator(
                                Modifier.tabIndicatorOffset(tabPositions[4]),
                                color = PrimaryMaroon,
                                height = 3.dp
                            )
                        }
                    }
                ) {
                    val tabs = listOf(
                        "Dashboard" to Icons.Outlined.Dashboard,
                        "Upload & Analyze" to Icons.Outlined.CloudUpload,
                        "Compare" to Icons.AutoMirrored.Outlined.CompareArrows,
                        "Reports" to Icons.Outlined.Description,
                        "Profile" to Icons.Outlined.Person
                    )
                    tabs.forEachIndexed { index, pair ->
                        val isSelected = index == 4
                        Tab(
                            selected = isSelected,
                            onClick = { 
                                when(index) {
                                    0 -> onNavigateToDashboard()
                                    1 -> onNavigateToAnalysis()
                                    2 -> onNavigateToCompare()
                                    3 -> onNavigateToReports()
                                }
                            },
                            text = { 
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier.padding(vertical = 12.dp)
                                ) {
                                    Icon(
                                        imageVector = pair.second,
                                        contentDescription = null,
                                        modifier = Modifier.size(16.dp),
                                        tint = if (isSelected) PrimaryMaroon else MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = pair.first, 
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        fontSize = 13.sp,
                                        color = if (isSelected) PrimaryMaroon else MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        )
                    }
                }
                HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
            }
        }
    ) { padding ->
        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600)) + slideInVertically(initialOffsetY = { 60 })
        ) {
            PullToRefreshBox(
                isRefreshing = uiState.isRefreshing,
                onRefresh = { viewModel.loadProfileAndNotes(isRefresh = true) },
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(MaterialTheme.colorScheme.background),
                    contentPadding = PaddingValues(20.dp),
                    verticalArrangement = Arrangement.spacedBy(24.dp)
                ) {
                    item {
                        Column {
                            Text(
                                text = "Workstation Settings",
                                fontSize = 32.sp,
                                fontWeight = FontWeight.Black,
                                color = MaterialTheme.colorScheme.onBackground,
                                lineHeight = 38.sp
                            )
                            Text(
                                text = "Manage your research identity, view overall performance metrics, and configure automated export pipelines.",
                                fontSize = 15.sp,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.padding(top = 12.dp),
                                lineHeight = 22.sp
                            )
                        }
                    }

                item {
                    ProfileMainCard(
                        name = uiState.name,
                        title = uiState.title,
                        email = uiState.email,
                        lab = uiState.laboratory,
                        institution = uiState.institution,
                        onEditClick = { viewModel.setEditingProfile(true) }
                    )
                }

                item {
                    ThemeSettingsCard(uiState.isDarkMode, viewModel::onToggleDarkMode)
                }

                item {
                    Column {
                        Text(
                            "Researcher Impact Metrics", 
                            fontSize = 18.sp, 
                            fontWeight = FontWeight.Black, 
                            color = MaterialTheme.colorScheme.onBackground
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Row(modifier = Modifier.fillMaxWidth()) {
                            SummaryStatCard("TOTAL ANALYSES", uiState.totalScans.toString(), Icons.Default.Science, Modifier.weight(1f))
                            Spacer(modifier = Modifier.width(16.dp))
                            SummaryStatCard("IMAGES PROCESSED", "386", Icons.Default.Image, Modifier.weight(1f))
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                        Row(modifier = Modifier.fillMaxWidth()) {
                            SummaryStatCard("REPORTS SHARED", "98", Icons.Default.Description, Modifier.weight(1f))
                            Spacer(modifier = Modifier.width(16.dp))
                            SummaryStatCard("AI ACCURACY", "99.4%", Icons.Default.Psychology, Modifier.weight(1f))
                        }
                    }
                }

                item {
                    DifferentialComparisonsSection()
                }

                item {
                    LabNotesSection(
                        notes = uiState.notes,
                        onNewNoteClick = { showAddNoteDialog = true },
                        onDeleteNote = viewModel::deleteNote
                    )
                }

                item {
                    FavoriteSamplesSection(
                        pinnedResults = uiState.pinnedResults,
                        onDeleteResult = viewModel::deletePinnedResult,
                        onResultClick = onNavigateToResults
                    )
                }

                item {
                    ExportPreferencesCard(
                        currentFormat = uiState.exportFormat,
                        overlayOriginal = uiState.overlayOriginal,
                        aiContourMap = uiState.aiContourMap,
                        onFormatChange = viewModel::updateExportFormat,
                        onOverlayChange = viewModel::toggleOverlayOriginal,
                        onAiMapChange = viewModel::toggleAiContourMap
                    )
                }

                if (uiState.recycleBin.isNotEmpty()) {
                    item {
                        RecycleBinSection(
                            items = uiState.recycleBin,
                            onRestore = viewModel::restoreItem,
                            onPermanentDelete = viewModel::permanentlyDeleteItem
                        )
                    }
                }

                item {
                    SignOutSection(onSignOut)
                    Spacer(modifier = Modifier.height(48.dp))
                }
            }
        }
    }
}
}

@Composable
fun ProfileMainCard(
    name: String,
    title: String,
    email: String,
    lab: String,
    institution: String,
    onEditClick: () -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth().shadow(8.dp, RoundedCornerShape(24.dp)),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(24.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Surface(
                    modifier = Modifier.size(80.dp),
                    shape = CircleShape,
                    color = PrimaryMaroon.copy(alpha = 0.08f)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(
                            name.split(" ").mapNotNull { it.firstOrNull() }.joinToString("").uppercase(), 
                            color = PrimaryMaroon, 
                            fontWeight = FontWeight.Black, 
                            fontSize = 28.sp
                        )
                    }
                }
                Spacer(modifier = Modifier.width(20.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(name, fontWeight = FontWeight.Black, fontSize = 22.sp, color = MaterialTheme.colorScheme.onSurface)
                    Surface(color = PrimaryMaroon.copy(0.1f), shape = RoundedCornerShape(6.dp), modifier = Modifier.padding(top = 4.dp)) {
                        Text(
                            title.uppercase(), 
                            fontSize = 10.sp, 
                            color = PrimaryMaroon, 
                            fontWeight = FontWeight.Black,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            letterSpacing = 1.sp
                        )
                    }
                    Text(email, fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 4.dp))
                }
                IconButton(
                    onClick = onEditClick,
                    modifier = Modifier.background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f), CircleShape).size(36.dp)
                ) {
                    Icon(Icons.Default.Edit, contentDescription = "Edit", modifier = Modifier.size(18.dp), tint = PrimaryMaroon)
                }
            }
            Spacer(modifier = Modifier.height(24.dp))
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
            Spacer(modifier = Modifier.height(24.dp))
            Row(modifier = Modifier.fillMaxWidth()) {
                InfoBlock(Icons.Default.Domain, "INSTITUTION", institution, Modifier.weight(1f))
                Spacer(modifier = Modifier.width(16.dp))
                InfoBlock(Icons.Default.Science, "LABORATORY", lab, Modifier.weight(1f))
            }
        }
    }
}

@Composable
fun EditProfileDialog(
    uiState: ProfileState,
    onDismiss: () -> Unit,
    onSave: (String, String, String, String) -> Unit
) {
    var name by remember { mutableStateOf(uiState.name) }
    var title by remember { mutableStateOf(uiState.title) }
    var institution by remember { mutableStateOf(uiState.institution) }
    var lab by remember { mutableStateOf(uiState.laboratory) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Edit Profile", fontWeight = FontWeight.Black) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                StainScopeTextField(value = name, onValueChange = { name = it }, label = "Name", placeholder = "Enter name")
                StainScopeTextField(value = title, onValueChange = { title = it }, label = "Title", placeholder = "Enter title")
                StainScopeTextField(value = institution, onValueChange = { institution = it }, label = "Institution", placeholder = "Enter institution")
                StainScopeTextField(value = lab, onValueChange = { lab = it }, label = "Laboratory", placeholder = "Enter laboratory")
            }
        },
        confirmButton = {
            TextButton(onClick = { onSave(name, title, institution, lab) }) {
                Text("Save", color = PrimaryMaroon, fontWeight = FontWeight.Bold)
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel", color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    )
}

@Composable
fun AddNoteDialog(
    onDismiss: () -> Unit,
    onAdd: (String, String) -> Unit
) {
    var title by remember { mutableStateOf("") }
    var content by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("New Research Note", fontWeight = FontWeight.Black) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                StainScopeTextField(value = title, onValueChange = { title = it }, label = "Title", placeholder = "Note title")
                StainScopeTextField(value = content, onValueChange = { content = it }, label = "Content", placeholder = "Note content", modifier = Modifier.height(120.dp))
            }
        },
        confirmButton = {
            TextButton(onClick = { if(title.isNotBlank()) onAdd(title, content) }) {
                Text("Add", color = PrimaryMaroon, fontWeight = FontWeight.Bold)
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel", color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    )
}

@Composable
fun ThemeSettingsCard(isDarkMode: Boolean, onToggleDarkMode: (Boolean) -> Unit) {
    Surface(
        modifier = Modifier.fillMaxWidth().shadow(4.dp, RoundedCornerShape(24.dp)),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = if (isDarkMode) Icons.Default.DarkMode else Icons.Default.LightMode,
                    contentDescription = null,
                    tint = PrimaryMaroon,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text("Display Theme", fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }
            Spacer(modifier = Modifier.height(16.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = if (isDarkMode) "Dark Mode Active" else "Light Mode Active",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "Toggle the global application theme.",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = isDarkMode,
                    onCheckedChange = onToggleDarkMode,
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = PrimaryMaroon,
                        uncheckedThumbColor = TextGray,
                        uncheckedTrackColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                )
            }
        }
    }
}

@Composable
fun InfoBlock(icon: ImageVector, label: String, value: String, modifier: Modifier) {
    Row(modifier = modifier, verticalAlignment = Alignment.Top) {
        Icon(icon, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f), modifier = Modifier.size(16.dp))
        Spacer(modifier = Modifier.width(10.dp))
        Column {
            Text(label, fontSize = 9.sp, fontWeight = FontWeight.Black, color = MaterialTheme.colorScheme.onSurfaceVariant, letterSpacing = 0.5.sp)
            Text(value, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface, lineHeight = 18.sp)
        }
    }
}

@Composable
fun SummaryStatCard(label: String, value: String, icon: ImageVector, modifier: Modifier) {
    Surface(
        modifier = modifier.shadow(2.dp, RoundedCornerShape(20.dp)),
        shape = RoundedCornerShape(20.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Surface(
                modifier = Modifier.size(32.dp),
                shape = RoundedCornerShape(8.dp),
                color = PrimaryMaroon.copy(alpha = 0.05f)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(icon, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(18.dp))
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text(value, fontSize = 24.sp, fontWeight = FontWeight.Black, color = MaterialTheme.colorScheme.onSurface)
            Text(label, fontSize = 10.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant, letterSpacing = 0.5.sp)
        }
    }
}

@Composable
fun DifferentialComparisonsSection() {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.AutoMirrored.Outlined.CompareArrows, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(12.dp))
                Text("Saved Differential Labs", fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }
            Spacer(modifier = Modifier.height(16.dp))
            ComparisonListItem("Control vs BMP-2 Induction", "EXP-8091 vs EXP-8092 (+25.6% Delta)")
            Spacer(modifier = Modifier.height(12.dp))
            ComparisonListItem("Day 7 vs Day 21 Progression", "EXP-7022 vs EXP-7045 (+42.1% Delta)")
        }
    }
}

@Composable
fun ComparisonListItem(title: String, subtitle: String) {
    Surface(
        modifier = Modifier.fillMaxWidth().clickable { },
        shape = RoundedCornerShape(12.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Row(modifier = Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(modifier = Modifier.size(8.dp).background(SuccessGreen, CircleShape))
            Spacer(modifier = Modifier.width(14.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(title, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                Text(subtitle, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Icon(Icons.Default.KeyboardArrowRight, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
fun LabNotesSection(
    notes: List<Note>,
    onNewNoteClick: () -> Unit,
    onDeleteNote: (String) -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.EditNote, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(22.dp))
                    Spacer(modifier = Modifier.width(12.dp))
                    Text("Research Notebook", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                }
                TextButton(onClick = onNewNoteClick) {
                    Text("+ New Note", color = PrimaryMaroon, fontSize = 13.sp, fontWeight = FontWeight.Black)
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            if (notes.isEmpty()) {
                Text("No notes found", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(vertical = 16.dp))
            } else {
                notes.forEach { note ->
                    NoteItem(
                        title = note.title,
                        date = note.date,
                        content = note.content,
                        onDelete = { onDeleteNote(note.id) }
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                }
            }
        }
    }
}

@Composable
fun NoteItem(title: String, date: String, content: String, onDelete: () -> Unit) {
    Surface(
        modifier = Modifier.fillMaxWidth().shadow(2.dp, RoundedCornerShape(16.dp)),
        shape = RoundedCornerShape(16.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(title, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface, modifier = Modifier.weight(1f))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(date, fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant, fontWeight = FontWeight.Black)
                    Spacer(modifier = Modifier.width(8.dp))
                    IconButton(onClick = onDelete, modifier = Modifier.size(24.dp)) {
                        Icon(Icons.Default.Delete, contentDescription = "Delete", tint = MaterialTheme.colorScheme.error, modifier = Modifier.size(16.dp))
                    }
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(content, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f), lineHeight = 18.sp)
        }
    }
}

@Composable
fun FavoriteSamplesSection(
    pinnedResults: List<PinnedResult>,
    onDeleteResult: (String) -> Unit,
    onResultClick: (String) -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.PushPin, contentDescription = null, tint = Color(0xFFFBC02D), modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(12.dp))
                Text("Pinned Lab Results", fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }
            Spacer(modifier = Modifier.height(16.dp))
            if (pinnedResults.isEmpty()) {
                Text("No pinned results", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(vertical = 16.dp))
            } else {
                pinnedResults.forEach { result ->
                    FavoriteItem(
                        title = result.title,
                        subtitle = result.subtitle,
                        onDelete = { onDeleteResult(result.id) },
                        onClick = { onResultClick(result.sampleId) }
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
fun FavoriteItem(title: String, subtitle: String, onDelete: () -> Unit, onClick: () -> Unit) {
    Surface(
        modifier = Modifier.fillMaxWidth().clickable { onClick() },
        shape = RoundedCornerShape(12.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(title, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                Text(subtitle, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            IconButton(onClick = onDelete) {
                Icon(Icons.Default.Delete, contentDescription = "Delete", tint = MaterialTheme.colorScheme.error, modifier = Modifier.size(18.dp))
            }
            Icon(Icons.AutoMirrored.Filled.OpenInNew, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(16.dp))
        }
    }
}

@Composable
fun ExportPreferencesCard(
    currentFormat: String,
    overlayOriginal: Boolean,
    aiContourMap: Boolean,
    onFormatChange: (String) -> Unit,
    onOverlayChange: (Boolean) -> Unit,
    onAiMapChange: (Boolean) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    val formats = listOf("Scientific PDF (Charts + Vector)", "Raw Data (CSV/Excel)", "Image Batch (TIFF/PNG)", "Combined Summary Report")

    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.SettingsSuggest, contentDescription = null, tint = PrimaryMaroon, modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(12.dp))
                Text("Automation Preferences", fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }
            Spacer(modifier = Modifier.height(20.dp))
            
            Text("DEFAULT EXPORT FORMAT", fontSize = 10.sp, fontWeight = FontWeight.Black, color = MaterialTheme.colorScheme.onSurfaceVariant, letterSpacing = 0.5.sp)
            Spacer(modifier = Modifier.height(8.dp))
            
            Box {
                Surface(
                    modifier = Modifier.fillMaxWidth().height(56.dp).clickable { expanded = true },
                    shape = RoundedCornerShape(12.dp),
                    color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
                ) {
                    Row(modifier = Modifier.padding(horizontal = 16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Text(currentFormat, modifier = Modifier.weight(1f), fontSize = 14.sp, color = MaterialTheme.colorScheme.onSurface)
                        Icon(Icons.Default.ExpandMore, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                    formats.forEach { format ->
                        DropdownMenuItem(
                            text = { Text(format) },
                            onClick = { 
                                onFormatChange(format)
                                expanded = false
                            }
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(20.dp))
            Row {
                ExportOption("Overlay Original", overlayOriginal, onOverlayChange, Modifier.weight(1f))
                ExportOption("AI Contour Map", aiContourMap, onAiMapChange, Modifier.weight(1f))
            }
        }
    }
}

@Composable
fun ExportOption(label: String, checked: Boolean, onCheckedChange: (Boolean) -> Unit, modifier: Modifier) {
    Row(modifier = modifier, verticalAlignment = Alignment.CenterVertically) {
        Checkbox(checked = checked, onCheckedChange = onCheckedChange, colors = CheckboxDefaults.colors(checkedColor = PrimaryMaroon))
        Spacer(modifier = Modifier.width(4.dp))
        Text(label, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f))
    }
}

@Composable
fun RecycleBinSection(
    items: List<DeletedItem>,
    onRestore: (String) -> Unit,
    onPermanentDelete: (String) -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.05f),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.error.copy(alpha = 0.1f))
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.DeleteSweep, contentDescription = null, tint = MaterialTheme.colorScheme.error, modifier = Modifier.size(22.dp))
                Spacer(modifier = Modifier.width(12.dp))
                Text("Recycle Bin", fontWeight = FontWeight.Bold, fontSize = 16.sp, color = MaterialTheme.colorScheme.error)
            }
            Text(
                "Items will be permanently deleted after 28 days.",
                fontSize = 11.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 4.dp, bottom = 16.dp)
            )
            
            items.forEach { item ->
                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(item.title, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                        Text("${item.type} • Deleted on ${SimpleDateFormat("MMM dd, yyyy", Locale.getDefault()).format(Date(item.deletedAt))}", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = { onRestore(item.id) }, modifier = Modifier.size(32.dp)) {
                            Icon(Icons.Default.History, contentDescription = "Restore", tint = PrimaryMaroon, modifier = Modifier.size(20.dp))
                        }
                        IconButton(onClick = { onPermanentDelete(item.id) }, modifier = Modifier.size(32.dp)) {
                            Icon(Icons.Default.DeleteForever, contentDescription = "Permanent Delete", tint = MaterialTheme.colorScheme.error, modifier = Modifier.size(20.dp))
                        }
                    }
                }
                if (items.last() != item) {
                    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f))
                }
            }
        }
    }
}

@Composable
fun SignOutSection(onSignOut: () -> Unit) {
    Button(
        onClick = onSignOut,
        modifier = Modifier.fillMaxWidth().height(56.dp),
        shape = RoundedCornerShape(16.dp),
        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.1f), contentColor = MaterialTheme.colorScheme.error),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.error.copy(alpha = 0.2f))
    ) {
        Icon(Icons.AutoMirrored.Filled.Logout, contentDescription = null, modifier = Modifier.size(20.dp))
        Spacer(modifier = Modifier.width(12.dp))
        Text("Logout", fontWeight = FontWeight.Black, fontSize = 15.sp)
    }
}
